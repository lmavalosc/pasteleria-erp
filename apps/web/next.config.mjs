/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: [
    '@pasteleria/shared-types',
    '@pasteleria/api-client',
    '@pasteleria/ui',
    '@repo/shared-types',
    '@repo/api-client',
    '@repo/ui',
  ],
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
      },
    ],
  },
  reactStrictMode: true,
};

export default nextConfig;
