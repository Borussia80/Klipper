const SCRIPT_INLINE_RE = /<script\b(?![^>]*\bsrc\s*=)(?![^>]*\btype\s*=\s*["']application\/json["'])([^>]*)>/g

export default defineNitroPlugin((nitroApp) => {
  nitroApp.hooks.hook('render:html', (html, { event }) => {
    const nonce = event.context.cspNonce as string | undefined
    if (!nonce) return

    const head = html.head as string[]
    const bodyAppend = html.bodyAppend as string[]

    html.head = head.map((chunk) =>
      chunk.replace(SCRIPT_INLINE_RE, `<script nonce="${nonce}"$1>`),
    )

    html.bodyAppend = bodyAppend.map((chunk) =>
      chunk.replace(SCRIPT_INLINE_RE, `<script nonce="${nonce}"$1>`),
    )
  })
})