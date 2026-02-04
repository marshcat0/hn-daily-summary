/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export
  output: 'export',

  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },

  // Base path for GitHub Pages (set via env var, empty for Vercel)
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || '',
  assetPrefix: process.env.NEXT_PUBLIC_BASE_PATH || '',

  // Trailing slashes for better static hosting compatibility
  trailingSlash: true,

  // Next.js 16+ uses turbopack by default
  // Disable if you encounter issues: turbopack: false,
};

export default nextConfig;
