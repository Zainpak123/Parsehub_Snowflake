/**
 * Backend API key for x-api-key header. Read from NEXT_PUBLIC_BACKEND_API_KEY.
 * Never hardcode the key in code.
 */
export function getBackendApiKey(): string | undefined {
  return process.env.NEXT_PUBLIC_BACKEND_API_KEY;
}

/**
 * Headers to send with every request to /api/* (backend).
 * Includes x-api-key when NEXT_PUBLIC_BACKEND_API_KEY is set.
 */
export function getApiHeaders(): Record<string, string> {
  const key = getBackendApiKey();
  if (!key) return {};
  return { 'x-api-key': key };
}

export function getApiBaseUrl(): string {
    const isServer = typeof window === 'undefined';

    const envUrl = process.env.NEXT_PUBLIC_API_BASE_URL ||
        process.env.NEXT_PUBLIC_BACKEND_URL ||
        (isServer ? process.env.BACKEND_API_URL || process.env.BACKEND_URL : undefined);

    if (process.env.NODE_ENV === 'production') {
        if (!envUrl) {
            throw new Error("CRITICAL: API base URL environment variable is missing in production. Please set NEXT_PUBLIC_API_BASE_URL or NEXT_PUBLIC_BACKEND_URL.");
        }
        if (envUrl.includes("localhost") || envUrl.includes("127.0.0.1") || envUrl.includes("0.0.0.0")) {
            throw new Error(`CRITICAL: Hardcoded localhost API URL (${envUrl}) detected in production.`);
        }
        return envUrl;
    }

    return envUrl || 'http://localhost:5000';
}

export function getFrontendApiUrl(): string {
    const envUrl = process.env.NEXT_PUBLIC_API_URL;

    if (process.env.NODE_ENV === 'production') {
        if (!envUrl) {
            // In production, Next.js relative paths work for frontend APIs if in browser
            if (typeof window !== 'undefined') {
                return '';
            }
            throw new Error("CRITICAL: Frontend API URL environment variable is missing in production. Please set NEXT_PUBLIC_API_URL.");
        }
        if (envUrl.includes("localhost") || envUrl.includes("127.0.0.1") || envUrl.includes("0.0.0.0")) {
            throw new Error(`CRITICAL: Hardcoded localhost Frontend API URL (${envUrl}) detected in production.`);
        }
        return envUrl;
    }

    return envUrl || 'http://localhost:3000';
}
