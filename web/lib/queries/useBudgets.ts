import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { supabase } from "@/lib/supabase"
import type { Database } from "@/types/database"

type Budget = Database["public"]["Tables"]["budgets"]["Row"]
type BudgetInsert = Database["public"]["Tables"]["budgets"]["Insert"]

export function useBudgets(year: number, month: number) {
  return useQuery({
    queryKey: ["budgets", year, month],
    queryFn: async (): Promise<Budget[]> => {
      const { data, error } = await supabase
        .from("budgets")
        .select("*")
        .eq("year", year)
        .eq("month", month)
        .order("category")
      if (error) throw error
      return data
    },
  })
}

export function useUpsertBudget() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: BudgetInsert) => {
      const { data, error } = await supabase
        .from("budgets")
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .upsert(payload as any, { onConflict: "category,year,month" })
        .select()
        .single()
      if (error) throw error
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["budgets"] })
    },
  })
}
