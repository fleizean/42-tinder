/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      'localhost',
      '127.0.0.1',
      process.env.NEXT_PUBLIC_BACKEND_API_URL || 'localhost',
      'images7.alphacoders.com',
      process.env.NEXT_AUTH_BACKEND_URL || 'backend',
    ],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8000',
        pathname: '/media/**',
      },
      {
        protocol: 'http',
        hostname: '127.0.0.1',
        port: '8000',
        pathname: '/media/**',
      },
      {
        protocol: 'https',
        hostname: 'images7.alphacoders.com',
        pathname: '/**',
      },
      {
        protocol: 'http',
        hostname: 'backend',
        port: '8000',
        pathname: '/media/**',
      }
    ]
  },
  reactStrictMode: true,
}

module.exports = nextConfig