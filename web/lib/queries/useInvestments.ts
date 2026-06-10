import { useQuery } from "@tanstack/react-query"
import { supabase } from "@/lib/supabase"
import type { Database } from "@/types/database"

type Investment = Database["public"]["Tables"]["investments"]["Row"]

export function useInvestments() {
  return useQuery({
    queryKey: ["investments"],
    queryFn: async (): Promise<Investment[]> => {
      const { data, error } = await supabase
        .from("investments")
        .select("*")
        .order("ticker")
      if (error) throw error
      return data
    },
  })
}

export type { Investment }
