/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL,
    NEXT_PUBLIC_BACKEND_API_KEY: process.env.NEXT_PUBLIC_BACKEND_API_KEY,
  },

  /**
   * Rewrite /api/:path* → backend /api/:path*
   *
   * Use NEXT_PUBLIC_BACKEND_URL on Railway (e.g. https://parsehub-backend-production.up.railway.app).
   * Do not set it without https://. Fallbacks: BACKEND_URL, BACKEND_API_URL.
   */
  async rewrites() {
    const backend =
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      process.env.BACKEND_URL ||
      process.env.BACKEND_API_URL ||
      '';

    if (!backend) {
      console.warn(
        '[next.config] NEXT_PUBLIC_BACKEND_URL is not set — /api/* rewrites disabled. ' +
        'Set NEXT_PUBLIC_BACKEND_URL in Railway → frontend service → Variables.'
      );
      return [];
    }

    const base = backend.replace(/\/$/, '');

    return [
      { source: '/api/:path*', destination: `${base}/api/:path*` },
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
