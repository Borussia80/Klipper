// Como o front alcança a API.
//
// Sem KLIPPER_API_PROXY_TARGET, o navegador chama a API direto em
// NUXT_PUBLIC_API_URL (dev local e perfil Docker, onde o Caddy já une as duas
// sob a mesma origem).
//
// Com KLIPPER_API_PROXY_TARGET (deploy na Vercel), o Nitro encaminha /api/** à
// API e o navegador só fala com a própria origem do front. Isso é necessário
// porque o refresh token é um cookie SameSite=Lax com Path=/api/v1/auth: com o
// front em *.vercel.app e a API em *.onrender.com, os sites são diferentes e o
// navegador nunca enviaria o cookie, derrubando a sessão a cada 15 minutos.

import type { NitroConfig } from 'nitropack/types'

type RouteRules = NonNullable<NitroConfig['routeRules']>

export interface ApiRouting {
  apiUrl: string
  routeRules: RouteRules
}

const LOCAL_HOSTS = new Set(['localhost', '127.0.0.1'])

function proxyOrigin(target: string): string {
  const url = new URL(target)
  if (url.protocol !== 'https:' && !LOCAL_HOSTS.has(url.hostname)) {
    throw new Error(`KLIPPER_API_PROXY_TARGET precisa ser https: recebido ${target}`)
  }
  return url.origin
}

export function resolveApiRouting(env: Record<string, string | undefined>): ApiRouting {
  const target = env.KLIPPER_API_PROXY_TARGET
  if (!target) {
    return { apiUrl: env.NUXT_PUBLIC_API_URL || 'http://localhost:3001', routeRules: {} }
  }
  return {
    apiUrl: '',
    routeRules: { '/api/**': { proxy: `${proxyOrigin(target)}/api/**` } },
  }
}
