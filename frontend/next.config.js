/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },

  /**
   * Rewrite /api/:path* → BACKEND_URL/api/:path*
   *
   * Evaluated at server start (not build time), so BACKEND_URL is read from
   * the runtime environment. Next.js App Router resolves app/api/ handlers
   * first; rewrites are a fallback for paths with no route file.
   *
   * Set on Railway (frontend service): BACKEND_URL or BACKEND_API_URL.
   */
  async rewrites() {
    const backendUrl =
      process.env.BACKEND_URL ||
      process.env.BACKEND_API_URL ||
      '';

    if (!backendUrl) {
      console.warn(
        '[next.config] BACKEND_URL is not set — /api/* rewrites disabled. ' +
        'Set BACKEND_URL in Railway → frontend service → Variables.'
      );
      return [];
    }

    const base = backendUrl.replace(/\/$/, '');

    return [
      {
        source: '/api/:path*',
        destination: `${base}/api/:path*`,
      },
    ];
  },

  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;
