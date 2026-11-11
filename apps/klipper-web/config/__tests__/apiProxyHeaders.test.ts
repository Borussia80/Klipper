// @vitest-environment node
//
// Na Vercel, a regra `/api/**` de `apiRouting.ts` roda em tempo de execução: o
// preset `vercel` do nitropack 2.13 só converte `redirect` e `headers` em
// rotas do CDN, e o Nitro atende `proxy` com o `proxyRequest` do h3. O login
// pelo celular depende de três coisas desse repasse:
//
// - `x-forwarded-host` chega à API com o domínio que o visitante abriu. É o
//   host que o HostAuthorization do Rails confere contra RAILS_ALLOWED_HOSTS.
// - o cookie do refresh token vai do navegador à API;
// - o `set-cookie` da API volta ao navegador sem `Domain`, preso à origem do
//   front.
//
// Uma atualização do h3 ou do Nitro que mude isso derruba a sessão em
// produção sem quebrar nenhum outro teste; este arquivo existe para pegar isso.

import { createServer, type IncomingHttpHeaders, type Server } from 'node:http'
import type { AddressInfo } from 'node:net'
import { createApp, eventHandler, proxyRequest, toNodeListener } from 'h3'
import { afterAll, beforeAll, describe, expect, it } from 'vitest'

function listen(server: Server): Promise<string> {
  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => {
      resolve(`http://127.0.0.1:${(server.address() as AddressInfo).port}`)
    })
  })
}

function close(server: Server): Promise<void> {
  return new Promise((resolve) => server.close(() => resolve()))
}

describe('proxy /api/** em tempo de execução (h3 proxyRequest)', () => {
  let received: IncomingHttpHeaders = {}
  let upstream: Server
  let front: Server
  let frontUrl: string

  beforeAll(async () => {
    upstream = createServer((req, res) => {
      received = req.headers
      res.setHeader('set-cookie', 'refresh_token=abc; Path=/api/v1/auth; HttpOnly; SameSite=Lax')
      res.setHeader('content-type', 'application/json')
      res.end('{"ok":true}')
    })
    const upstreamUrl = await listen(upstream)

    const app = createApp()
    app.use(
      '/api',
      eventHandler((event) => proxyRequest(event, `${upstreamUrl}/api${event.path}`)),
    )
    front = createServer(toNodeListener(app))
    frontUrl = await listen(front)
  })

  afterAll(async () => {
    await close(front)
    await close(upstream)
  })

  it('repassa à API o x-forwarded-host do domínio visitado e o cookie de sessão', async () => {
    const response = await fetch(`${frontUrl}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: {
        'x-forwarded-host': 'klipper-app.vercel.app',
        'x-forwarded-proto': 'https',
        cookie: 'refresh_token=old',
      },
    })

    expect(response.status).toBe(200)
    expect(received['x-forwarded-host']).toBe('klipper-app.vercel.app')
    expect(received['x-forwarded-proto']).toBe('https')
    expect(received.cookie).toBe('refresh_token=old')
    // O Host do front não é reaproveitado: a API recebe o próprio host.
    expect(received.host).toMatch(/^127\.0\.0\.1:\d+$/)
  })

  it('devolve o set-cookie da API sem Domain, preso à origem do front', async () => {
    const response = await fetch(`${frontUrl}/api/v1/auth/refresh`, { method: 'POST' })

    const cookie = response.headers.get('set-cookie')
    expect(cookie).toContain('refresh_token=abc')
    expect(cookie).toContain('Path=/api/v1/auth')
    expect(cookie).not.toMatch(/domain=/i)
  })
})
