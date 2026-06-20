"use client"

import { useEffect, useState } from "react"
import { useDebounce } from "@/lib/hooks/useDebounce"
import { supabase } from "@/lib/supabase"
import { applyRules, type Rule } from "@/lib/queries/useRules"

export interface CategorySuggestion {
  category:   string
  confidence: number
  source:     string
}

export function useCategorySuggest(
  notes: string,
  amount = 0,
  rules:  Rule[] = [],
): CategorySuggestion | null {
  const debounced = useDebounce(notes, 350)
  const [suggestion, setSuggestion] = useState<CategorySuggestion | null>(null)

  useEffect(() => {
    if (!debounced || debounced.trim().length < 3) {
      setSuggestion(null)
      return
    }

    // 1. Check deterministic rules first (no API call needed)
    const ruleMatch = applyRules(debounced, amount, rules)
    if (ruleMatch) {
      setSuggestion({ category: ruleMatch, confidence: 1, source: "rule" })
      return
    }

    // 2. Fall back to fuzzy API
    const controller = new AbortController()

    async function fetchSuggestion() {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        const token = session?.access_token
        if (!token) return

        const apiBase = process.env.NEXT_PUBLIC_API_URL
        if (!apiBase) return

        const res = await fetch(`${apiBase}/category/suggest`, {
          method:  "POST",
          headers: {
            "Content-Type":  "application/json",
            "Authorization": `Bearer ${token}`,
          },
          body:   JSON.stringify({ notes: debounced }),
          signal: controller.signal,
        })

        if (!res.ok) return
        const json = await res.json() as CategorySuggestion
        setSuggestion(json)
      } catch {
        // Silent fail — offline or API unavailable
      }
    }

    void fetchSuggestion()
    return () => controller.abort()
  }, [debounced, amount, rules])

  return suggestion
}
