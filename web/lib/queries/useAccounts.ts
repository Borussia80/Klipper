import { useQuery } from "@tanstack/react-query"
import { supabase } from "@/lib/supabase"
import type { Database } from "@/types/database"

type BankAccount = Database["public"]["Tables"]["bank_accounts"]["Row"]
type CreditCard = Database["public"]["Tables"]["credit_cards"]["Row"]

export function useBankAccounts() {
  return useQuery({
    queryKey: ["bank-accounts"],
    queryFn: async (): Promise<BankAccount[]> => {
      const { data, error } = await supabase
        .from("bank_accounts")
        .select("*")
        .eq("is_active", true)
        .order("name")
      if (error) throw error
      return data
    },
  })
}

export function useCreditCards() {
  return useQuery({
    queryKey: ["credit-cards"],
    queryFn: async (): Promise<CreditCard[]> => {
      const { data, error } = await supabase
        .from("credit_cards")
        .select("*")
        .eq("is_active", true)
        .order("name")
      if (error) throw error
      return data
    },
  })
}
