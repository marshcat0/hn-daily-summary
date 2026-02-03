/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export for GitHub Pages
  output: 'export',

  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },

  // Base path for GitHub Pages (uncomment if deploying to username.github.io/repo-name)
  // basePath: '/hn-daily-summary',

  // Trailing slashes for better static hosting compatibility
  trailingSlash: true,

  // Next.js 16+ uses turbopack by default
  // Disable if you encounter issues: turbopack: false,
};

export default nextConfig;
