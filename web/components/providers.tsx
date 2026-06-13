"use client"

import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { supabase } from "@/lib/supabase"

export function Providers({ children }: { children: React.ReactNode }) {
  // O link de recuperação pode cair em qualquer rota (Supabase usa a Site URL como
  // fallback quando o redirect_to não está na allowlist). Onde quer que caia, a sessão
  // de recovery é global — redirecionamos para /login, que tem a UI de nova senha.
  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event) => {
      if (event === "PASSWORD_RECOVERY" && window.location.pathname !== "/login") {
        window.location.assign("/login#type=recovery")
      }
    })
    return () => subscription.unsubscribe()
  }, [])

  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60_000,
            retry: 1,
          },
        },
      })
  )
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}
