import { createClient } from "@supabase/supabase-js"
import type { Database } from "@/types/database"

export const supabase = createClient<Database>(
  process.env.NEXT_PUBLIC_SUPABASE_URL ?? "http://localhost",
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "placeholder"
)
