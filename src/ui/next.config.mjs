/** @type {import('next').NextConfig} */
const nextConfig = {
  // Disable Turbopack for Windows compatibility with better-sqlite3
  experimental: {
    turbopack: false,
  },
  // Global deployment settings
  turbopack: {
    root: process.cwd(),
  },
};

export default nextConfig;
