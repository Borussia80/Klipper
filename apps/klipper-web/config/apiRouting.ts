// Como o front alcança a API.
//
// Sem proxy, o navegador chama a API direto em NUXT_PUBLIC_API_URL (dev local
// e perfil Docker, onde o Caddy já une as duas sob a mesma origem).
//
// Com proxy, o Nitro encaminha /api/** à API e o navegador só fala com a
// própria origem do front. Isso é necessário porque o refresh token é um
// cookie SameSite=Lax com Path=/api/v1/auth: com o front em *.vercel.app e a
// API em *.onrender.com, os sites são diferentes e o navegador nunca enviaria o
// cookie, derrubando a sessão a cada 15 minutos.
//
// O destino do proxy é KLIPPER_API_PROXY_TARGET ou, num build da Vercel, o
// próprio NUXT_PUBLIC_API_URL (já configurado no projeto). A chave pública é
// `apiBase`, não `apiUrl`: assim a NUXT_PUBLIC_API_URL presente em tempo de
// execução na Vercel não sobrepõe a mesma origem decidida no build.

import type { NitroConfig } from 'nitropack/types'

type RouteRules = NonNullable<NitroConfig['routeRules']>

export interface ApiRouting {
  apiBase: string
  routeRules: RouteRules
}

const LOCAL_HOSTS = new Set(['localhost', '127.0.0.1'])

function proxyOrigin(target: string): string {
  const url = new URL(target)
  if (url.protocol !== 'https:' && !LOCAL_HOSTS.has(url.hostname)) {
    throw new Error(`O destino do proxy da API precisa ser https: recebido ${target}`)
  }
  return url.origin
}

function proxyTarget(env: Record<string, string | undefined>): string | undefined {
  if (env.KLIPPER_API_PROXY_TARGET) return env.KLIPPER_API_PROXY_TARGET
  if (env.VERCEL && env.NUXT_PUBLIC_API_URL?.startsWith('https://')) return env.NUXT_PUBLIC_API_URL
  return undefined
}

export function resolveApiRouting(env: Record<string, string | undefined>): ApiRouting {
  const target = proxyTarget(env)
  if (!target) {
    return { apiBase: env.NUXT_PUBLIC_API_URL || 'http://localhost:3001', routeRules: {} }
  }
  return {
    apiBase: '',
    routeRules: { '/api/**': { proxy: `${proxyOrigin(target)}/api/**` } },
  }
}
