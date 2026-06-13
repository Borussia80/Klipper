import { createBrowserClient } from "@supabase/ssr"
import type { Database } from "@/types/database"

// Cliente de browser do @supabase/ssr: persiste a sessão em COOKIES (não
// localStorage). É o que permite ao middleware (proxy.ts, server-side) enxergar
// o usuário autenticado — sem isso o login completa mas o middleware redireciona
// de volta para /login por não achar a sessão.
//
// Os métodos de cookie são lazy (só tocam document.cookie no browser), então a
// criação no topo do módulo é SSR-safe para o build estático do Next.
export const supabase = createBrowserClient<Database>(
  process.env.NEXT_PUBLIC_SUPABASE_URL || "https://placeholder.supabase.co",
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.placeholder",
)
