/**
 * _proxy.ts — Central server-side proxy utility
 *
 * All Next.js API route handlers call `proxyToBackend()` from here.
 * Browser never touches the Flask domain — only hits same-origin /api/*.
 *
 * Required Railway env vars on the FRONTEND service (server-side only):
 *   BACKEND_API_URL=https://<backend>.up.railway.app   ← primary
 *   BACKEND_URL=https://<backend>.up.railway.app        ← alias accepted
 *   BACKEND_API_KEY=<your-key>
 *
 * Error surface:
 *   502 - Flask is down / ECONNREFUSED / network unreachable
 *   503 - Flask booted but DB not ready
 *   504 - Request timed out
 *   5xx - Flask returned an error (forwarded as-is)
 *
 * Retry behaviour:
 *   proxyToBackend() retries idempotent methods (GET/HEAD/DELETE) up to
 *   MAX_RETRIES times with exponential back-off before giving up.
 *   Non-idempotent methods (POST/PUT/PATCH) are never retried automatically.
 */

import { NextRequest, NextResponse } from 'next/server';

const TIMEOUT_MS  = 30_000;
const MAX_RETRIES = 2;          // 3 total attempts for idempotent requests

// ── Backend URL resolution (LAZY — evaluated per-call, not at module load) ─
// Resolving at module load time throws during Next.js cold-start when the env
// var is missing, crashing every API route before a single request arrives.
function getBackendBase(): string {
    const url =
        process.env.BACKEND_API_URL ||
        process.env.BACKEND_URL ||
        '';

    if (!url) {
        if (process.env.NODE_ENV === 'production') {
            // Log clearly so the Railway build log surfaces the missing var.
            console.error(
                '[proxy] FATAL: BACKEND_API_URL is not set. ' +
                'Go to Railway → frontend service → Variables and add it.'
            );
        }
        // Fall back to localhost for local dev
        return 'http://localhost:5000';
    }

    if (
        process.env.NODE_ENV === 'production' &&
        (url.includes('localhost') || url.includes('127.0.0.1') || url.includes('0.0.0.0'))
    ) {
        console.error(
            `[proxy] WARNING: BACKEND_API_URL points to a local address in production: ${url}`
        );
    }

    return url.replace(/\/$/, '');
}

function getApiKey(): string {
    return process.env.NEXT_PUBLIC_BACKEND_API_KEY || process.env.BACKEND_API_KEY || '';
}

// ── Helper: build a structured error payload ───────────────────────────────
function backendError(
    message: string,
    status: number,
    details?: string,
    backendStatus?: number
): NextResponse {
    return NextResponse.json(
        {
            error: message,
            backend_status: backendStatus ?? null,
            details: details ?? null,
            backend_url: getBackendBase(),   // shown in dev tools to debug mis-config
        },
        { status }
    );
}

// ── Helper: one-shot health check (used only after a network failure) ──────
// The caller passes `backendBase` so we reuse the already-resolved value and
// avoid a second env-var lookup.  This function NEVER throws.
async function checkBackendHealth(
    backendBase: string,
    apiKey: string
): Promise<{ ok: boolean; detail: string }> {
    try {
        const res = await fetch(`${backendBase}/api/health`, {
            headers: { Authorization: `Bearer ${apiKey}` },
            signal: AbortSignal.timeout(5_000),
        });
        if (res.ok) return { ok: true, detail: 'ok' };
        return { ok: false, detail: `Flask /api/health returned ${res.status}` };
    } catch (e) {
        return {
            ok: false,
            detail: e instanceof Error ? e.message : String(e),
        };
    }
}

// ── Exponential back-off sleep ─────────────────────────────────────────────
function sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ── Core proxy function ────────────────────────────────────────────────────
/**
 * Forward a Next.js route request to the Flask backend.
 *
 * @param req            - Incoming NextRequest
 * @param backendPath    - Path on Flask, e.g. "/api/projects"
 * @param queryOverrides - Optional URLSearchParams (replaces request search params)
 */
export async function proxyToBackend(
    req: NextRequest,
    backendPath: string,
    queryOverrides?: URLSearchParams
): Promise<NextResponse> {
    // Resolve lazily — never throws even if env var is absent
    const backendBase = getBackendBase();
    const apiKey      = getApiKey();

    const qs          = queryOverrides ?? req.nextUrl.searchParams;
    const queryString = qs.toString();
    const targetUrl   = `${backendBase}${backendPath}${queryString ? `?${queryString}` : ''}`;
    const method      = req.method.toUpperCase();

    console.log(`[proxy] ${method} ${req.nextUrl.pathname} → ${targetUrl}`);

    // Read body once for mutating methods
    let body: string | undefined;
    if (!['GET', 'HEAD', 'DELETE'].includes(method)) {
        try { body = await req.text(); } catch { body = undefined; }
    }

    // Determine if this endpoint requires authentication
    // Public read-only endpoints don't need auth (handled server-side anyway)
    const isPublicEndpoint = method === 'GET' && (
        backendPath.startsWith('/api/filters') ||
        backendPath.startsWith('/api/metadata') ||
        backendPath.startsWith('/api/projects?') ||
        backendPath.startsWith('/api/health')
    );

    const outgoingHeaders: Record<string, string> = {
        'Content-Type':  'application/json',
        'Accept':        'application/json',
        // Only add API key for non-public endpoints or mutating operations
        ...(!isPublicEndpoint && apiKey ? { 'Authorization': `Bearer ${apiKey}`, 'x-api-key': apiKey } : {}),
    };

    // Idempotent methods are safe to retry; mutating ones are not
    const isIdempotent = ['GET', 'HEAD', 'DELETE'].includes(method);
    const maxAttempts  = isIdempotent ? MAX_RETRIES + 1 : 1;

    let lastError: unknown;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        if (attempt > 1) {
            const delayMs = 500 * 2 ** (attempt - 2);   // 500 ms, 1 000 ms, …
            console.log(`[proxy] Retry ${attempt - 1}/${MAX_RETRIES} in ${delayMs}ms for ${targetUrl}`);
            await sleep(delayMs);
        }

        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

        try {
            const backendResponse = await fetch(targetUrl, {
                method,
                headers: outgoingHeaders,
                body: body || undefined,
                signal: controller.signal,
            });

            clearTimeout(timer);

            const contentType = backendResponse.headers.get('content-type') ?? '';
            let responseData: unknown;
            if (contentType.includes('application/json')) {
                responseData = await backendResponse.json();
            } else {
                const raw = await backendResponse.text();
                responseData = { raw };
            }

            if (!backendResponse.ok) {
                const errMsg =
                    (responseData as Record<string, string>)?.error ??
                    `Backend returned ${backendResponse.status}`;

                console.error(`[proxy] ${backendResponse.status} from ${targetUrl}: ${errMsg}`);

                if (backendResponse.status === 503) {
                    return backendError(
                        'Database is not ready. The backend is booting — please retry in a moment.',
                        503,
                        errMsg,
                        503
                    );
                }

                // 5xx errors are retried (for idempotent methods); 4xx are not
                if (backendResponse.status >= 500 && attempt < maxAttempts) {
                    lastError = new Error(errMsg);
                    continue;
                }

                return backendError(errMsg, backendResponse.status, undefined, backendResponse.status);
            }

            return NextResponse.json(responseData, { status: backendResponse.status });

        } catch (err: unknown) {
            clearTimeout(timer);
            lastError = err;

            if (err instanceof Error && (err.name === 'AbortError' || err.name === 'TimeoutError')) {
                console.error(`[proxy] Timeout after ${TIMEOUT_MS}ms for ${targetUrl}`);
                if (attempt < maxAttempts) continue;
                return backendError(
                    'Backend request timed out. The server may be overloaded — please retry.',
                    504
                );
            }

            // Non-timeout network error — retry if attempts remain
            if (attempt < maxAttempts) continue;

            // All retries exhausted: run a one-shot health check to give a
            // meaningful error message instead of an opaque 502.
            const health = await checkBackendHealth(backendBase, apiKey);
            const detail  = err instanceof Error ? err.message : String(err);

            console.error(`[proxy] Network error for ${targetUrl}:`, detail);
            console.error(`[proxy] Flask health: ${health.detail}`);

            if (!health.ok) {
                return backendError(
                    'Flask backend is unreachable. It may still be booting on Railway.',
                    502,
                    health.detail
                );
            }

            return backendError('Backend request failed. Please try again.', 502, detail);
        }
    }

    // Should never reach here, but TypeScript requires a return
    const detail = lastError instanceof Error ? lastError.message : String(lastError);
    return backendError('All retry attempts failed.', 502, detail);
}
