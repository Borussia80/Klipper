import { createClient } from "@supabase/supabase-js"
import type { Database } from "@/types/database"

// SSR-safe: supabase-js accesses localStorage at init time when a real URL is present.
// Provide a no-op storage on the server so Next.js static generation doesn't crash.
const safeStorage =
  typeof window !== "undefined"
    ? window.localStorage
    : {
        getItem: (_key: string) => null,
        setItem: (_key: string, _val: string) => {},
        removeItem: (_key: string) => {},
      }

export const supabase = createClient<Database>(
  process.env.NEXT_PUBLIC_SUPABASE_URL ?? "http://localhost",
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "placeholder",
  { auth: { storage: safeStorage } }
)
