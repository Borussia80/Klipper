import { createServerClient } from "@supabase/ssr"
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

const PUBLIC_ROUTES = ["/login", "/auth/callback"]

export async function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Resposta base — o createServerClient pode precisar reescrever cookies
  // (refresh de token); por isso devolvemos ESTA resposta, não NextResponse.next() novo.
  let response = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
          response = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, options),
          )
        },
      },
    },
  )

  // IMPORTANTE: getUser() valida o JWT junto ao Supabase. Não use getSession()
  // no servidor — ele só lê o cookie sem validar a assinatura.
  const { data: { user } } = await supabase.auth.getUser()

  const isPublic = PUBLIC_ROUTES.some((r) => pathname.startsWith(r))
  if (!user && !isPublic) {
    return NextResponse.redirect(new URL("/login", request.url))
  }

  return response
}

export const config = {
  matcher: [
    /*
     * Protege todas as rotas exceto:
     * - _next/static, _next/image (assets internos Next.js)
     * - favicon.ico, manifest.json, icons (PWA)
     * - /login, /auth/callback (fluxo de auth)
     */
    "/((?!_next/static|_next/image|favicon.ico|manifest.json|icon-|login|auth).*)",
  ],
}
