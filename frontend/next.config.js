/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      'localhost',
      '127.0.0.1',
      process.env.NEXT_PUBLIC_BACKEND_HOST || 'localhost',
      'images7.alphacoders.com'
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
      }
    ]
  },
  reactStrictMode: true,
}

module.exports = nextConfig