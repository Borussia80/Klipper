import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"
import { createClient } from "@supabase/supabase-js"

const PUBLIC_ROUTES = ["/login", "/auth/callback"]

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Rotas públicas: deixa passar
  if (PUBLIC_ROUTES.some((r) => pathname.startsWith(r))) {
    return NextResponse.next()
  }

  // Verifica sessão via cookie Supabase
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
  const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

  const accessToken =
    request.cookies.get("sb-access-token")?.value ??
    request.cookies.get(`sb-${supabaseUrl.split("//")[1].split(".")[0]}-auth-token`)?.value

  if (!accessToken) {
    return NextResponse.redirect(new URL("/login", request.url))
  }

  // Verifica token válido (lightweight — não faz round-trip ao DB)
  try {
    const client = createClient(supabaseUrl, supabaseKey)
    const { data: { user }, error } = await client.auth.getUser(accessToken)
    if (error || !user) {
      return NextResponse.redirect(new URL("/login", request.url))
    }
  } catch {
    return NextResponse.redirect(new URL("/login", request.url))
  }

  return NextResponse.next()
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
