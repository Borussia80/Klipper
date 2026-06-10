"use client"

import { useState } from "react"
import { PageHeader } from "@/components/ui/page-header"
import { KCard } from "@/components/ui/kcard"
import { SkeletonCard } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/ui/empty-state"
import { useBudgets } from "@/lib/queries/useBudgets"
import { useTransactions } from "@/lib/queries/useTransactions"
import { fmtBRL } from "@/lib/utils"
import { cn } from "@/lib/utils"

const MESES_PT = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

function useNow() {
  const now = new Date()
  return { year: now.getFullYear(), month: now.getMonth() + 1 }
}

function ProgressBar({ pct }: { pct: number }) {
  const clamped = Math.min(pct, 100)
  const over = pct > 100
  return (
    <div className="w-full h-1.5 rounded-full bg-[var(--layer)] overflow-hidden">
      <div
        className={cn(
          "h-full rounded-full transition-all",
          over ? "bg-[var(--neg)]" : "bg-[var(--brass)]"
        )}
        style={{ width: `${clamped}%` }}
      />
    </div>
  )
}

export default function OrcamentoPage() {
  const { year: initYear, month: initMonth } = useNow()
  const [year, setYear] = useState(initYear)
  const [month, setMonth] = useState(initMonth)

  const { data: budgets, isLoading: budgetLoading } = useBudgets(year, month)
  const { data: txs, isLoading: txLoading } = useTransactions(year, month)

  function prevMonth() {
    if (month === 1) { setMonth(12); setYear(y => y - 1) }
    else setMonth(m => m - 1)
  }
  function nextMonth() {
    if (month === 12) { setMonth(1); setYear(y => y + 1) }
    else setMonth(m => m + 1)
  }

  // Compute spending per category
  const spentMap: Record<string, number> = {}
  txs?.filter(t => t.type === "GASTO").forEach(t => {
    spentMap[t.category] = (spentMap[t.category] ?? 0) + t.amount
  })

  const isLoading = budgetLoading || txLoading
  const subtitle = `${MESES_PT[month - 1]} ${year}`

  const totalLimit = budgets?.reduce((s, b) => s + b.monthly_limit, 0) ?? 0
  const totalSpent = budgets?.reduce((s, b) => s + (spentMap[b.category] ?? 0), 0) ?? 0

  return (
    <div className="p-4 md:p-6 max-w-3xl mx-auto">
      <PageHeader title="Orçamento" />

      {/* Month nav */}
      <div className="flex items-center gap-2 mb-6">
        <button onClick={prevMonth} className="p-1 rounded hover:bg-[var(--layer)] text-[var(--ink-3)]">‹</button>
        <span className="text-sm font-medium text-[var(--ink)] min-w-[80px] text-center">{subtitle}</span>
        <button onClick={nextMonth} className="p-1 rounded hover:bg-[var(--layer)] text-[var(--ink-3)]">›</button>
      </div>

      {/* Summary */}
      {!isLoading && budgets && budgets.length > 0 && (
        <KCard variant="surface" className="mb-4">
          <div className="flex justify-between text-sm">
            <div>
              <p className="text-xs text-[var(--ink-3)] uppercase tracking-wide mb-1">Total gasto</p>
              <p className={cn("text-xl font-semibold tabular", totalSpent > totalLimit ? "text-[var(--neg)]" : "text-[var(--ink)]")}>
                {fmtBRL(totalSpent)}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-[var(--ink-3)] uppercase tracking-wide mb-1">Orçado</p>
              <p className="text-xl font-semibold tabular text-[var(--ink)]">{fmtBRL(totalLimit)}</p>
            </div>
          </div>
          <ProgressBar pct={(totalSpent / totalLimit) * 100} />
        </KCard>
      )}

      {/* Per-category budgets */}
      {isLoading ? (
        <div className="flex flex-col gap-3">
          {Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} className="h-20" />)}
        </div>
      ) : !budgets || budgets.length === 0 ? (
        <EmptyState
          title="Nenhum orçamento configurado"
          description="Configure limites por categoria pelo app Streamlit."
        />
      ) : (
        <div className="flex flex-col gap-3">
          {budgets.map((b) => {
            const spent = spentMap[b.category] ?? 0
            const pct = b.monthly_limit > 0 ? (spent / b.monthly_limit) * 100 : 0
            const over = spent > b.monthly_limit

            return (
              <KCard key={b.id} variant="surface">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-[var(--ink)]">{b.category}</span>
                  <div className="text-xs tabular text-right">
                    <span className={cn("font-medium", over ? "text-[var(--neg)]" : "text-[var(--ink)]")}>
                      {fmtBRL(spent)}
                    </span>
                    <span className="text-[var(--ink-4)]"> / {fmtBRL(b.monthly_limit)}</span>
                  </div>
                </div>
                <ProgressBar pct={pct} />
                <p className="text-xs text-[var(--ink-4)] mt-1">
                  {over
                    ? `⚠ Estouro de ${fmtBRL(spent - b.monthly_limit)}`
                    : `${fmtBRL(b.monthly_limit - spent)} disponível`}
                </p>
              </KCard>
            )
          })}
        </div>
      )}
    </div>
  )
}
