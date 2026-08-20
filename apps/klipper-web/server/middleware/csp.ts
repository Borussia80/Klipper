import crypto from 'node:crypto'

function generateNonce(): string {
  return crypto.randomBytes(16).toString('base64')
}

export default defineEventHandler((event) => {
  const config = useRuntimeConfig(event)
  const isDev = process.env.NODE_ENV !== 'production'

  const apiUrl = (config.public.apiUrl as string) || ''

  let connectSrc = "'self'"
  if (apiUrl && !apiUrl.startsWith('/')) {
    try {
      connectSrc += ` ${new URL(apiUrl).origin}`
    } catch {
      connectSrc += ` ${apiUrl}`
    }
  }

  if (isDev) {
    connectSrc += ' ws:'
  }

  const nonce = generateNonce()
  event.context.cspNonce = nonce

  const scriptSrc = isDev
    ? "'self' 'unsafe-inline'"
    : `'self' 'nonce-${nonce}'`

  const csp = [
    `default-src 'self'`,
    `script-src ${scriptSrc}`,
    `style-src 'self' 'unsafe-inline'`,
    `img-src 'self' data:`,
    `font-src 'self'`,
    `connect-src ${connectSrc}`,
    `frame-ancestors 'none'`,
    `base-uri 'self'`,
    `form-action 'self'`,
    `upgrade-insecure-requests`,
  ].join('; ')

  setResponseHeader(event, 'Content-Security-Policy', csp)
})