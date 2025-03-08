/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      'localhost',
      '127.0.0.1',
       process.env.NEXT_PUBLIC_BACKEND_URL?.replace(/https?:\/\//, '') || 'localhost',
      'images7.alphacoders.com'
    ],
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '5187',
        pathname: '/uploads/**',
      },
      {
        protocol: 'http',
        hostname: '127.0.0.1',
        port: '5187',
        pathname: '/uploads/**',
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