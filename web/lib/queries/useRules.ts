import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { supabase } from "@/lib/supabase"
import type { Database } from "@/types/database"

export type Rule       = Database["public"]["Tables"]["categorization_rules"]["Row"]
export type RuleInsert = Database["public"]["Tables"]["categorization_rules"]["Insert"]

export const RULE_FIELDS    = ["notes", "amount"] as const
export const RULE_OPERATORS = ["contains", "starts_with", "equals", "greater_than", "less_than", "regex"] as const

export type RuleField    = typeof RULE_FIELDS[number]
export type RuleOperator = typeof RULE_OPERATORS[number]

/** Applies rules (sorted by priority ASC) to description + amount. Returns category or null. */
export function applyRules(notes: string, amount: number, rules: Rule[]): string | null {
  const active = [...rules]
    .filter(r => r.is_active)
    .sort((a, b) => a.priority - b.priority)

  for (const r of active) {
    const target = r.field === "notes" ? notes.toLowerCase() : String(amount)
    const pat    = r.value.toLowerCase()
    let   match  = false

    switch (r.operator) {
      case "contains":     match = target.includes(pat);       break
      case "starts_with":  match = target.startsWith(pat);     break
      case "equals":       match = target === pat;              break
      case "greater_than": match = amount > Number(r.value);   break
      case "less_than":    match = amount < Number(r.value);   break
      case "regex":
        try { match = new RegExp(r.value, "i").test(notes) } catch { /* skip invalid regex */ }
        break
    }

    if (match) return r.category
  }
  return null
}

export function useRules() {
  return useQuery({
    queryKey: ["rules"],
    queryFn: async (): Promise<Rule[]> => {
      const { data, error } = await supabase
        .from("categorization_rules")
        .select("*")
        .order("priority", { ascending: true })
      if (error) throw error
      return data
    },
  })
}

export function useCreateRule() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (payload: RuleInsert): Promise<Rule> => {
      const { data, error } = await supabase
        .from("categorization_rules")
        .insert(payload)
        .select()
        .single()
      if (error) throw error
      return data
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["rules"] }) },
  })
}

export function useDeleteRule() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase.from("categorization_rules").delete().eq("id", id)
      if (error) throw error
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["rules"] }) },
  })
}

export function useToggleRule() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, is_active }: { id: string; is_active: boolean }) => {
      const { error } = await supabase
        .from("categorization_rules")
        .update({ is_active })
        .eq("id", id)
      if (error) throw error
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["rules"] }) },
  })
}
