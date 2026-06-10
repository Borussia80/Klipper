import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  // Serwist (PWA) será adicionado na Fase 1 final
  // por ora, apenas configurações base
  experimental: {
    typedRoutes: true,
  },
}

export default nextConfig
