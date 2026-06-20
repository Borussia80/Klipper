"use client"

import { useState, useEffect } from "react"
import { PageHeader } from "@/components/ui/page-header"
import { KCard } from "@/components/ui/kcard"
import { SkeletonCard } from "@/components/ui/skeleton"
import { BudgetSetupDialog } from "@/components/ui/budget-setup-dialog"
import { useBudgets, useUpsertBudget } from "@/lib/queries/useBudgets"
import { useTransactions } from "@/lib/queries/useTransactions"
import { fmtBRL } from "@/lib/utils"
import { cn } from "@/lib/utils"
import { supabase } from "@/lib/supabase"

const MESES_PT = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

function useNow() {
  const now = new Date()
  return { year: now.getFullYear(), month: now.getMonth() + 1 }
}

function envelopeColor(pct: number): string {
  if (pct > 100) return "var(--neg)"      // red — over budget
  if (pct > 90)  return "#F97316"          // orange — close
  if (pct > 70)  return "#F59E0B"          // amber — caution
  return "var(--pos)"                      // green — safe
}

function EnvelopeBar({ pct }: { pct: number }) {
  const clamped = Math.min(pct, 100)
  return (
    <div className="w-full h-2 rounded-full bg-[var(--layer)] overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-300"
        style={{ width: `${clamped}%`, background: envelopeColor(pct) }}
      />
    </div>
  )
}

interface AlertBadge {
  category: string
  pct_used: number
  overbudget: boolean
  message: string
}

export default function OrcamentoPage() {
  const { year: initYear, month: initMonth } = useNow()
  const [year,  setYear]  = useState(initYear)
  const [month, setMonth] = useState(initMonth)
  const [setupOpen, setSetupOpen]   = useState(false)
  const [alerts,    setAlerts]      = useState<AlertBadge[]>([])
  const [projections, setProjections] = useState<Record<string, number>>({})

  const { data: budgets, isLoading: budgetLoading, error: budgetError } = useBudgets(year, month)
  const { data: txs,     isLoading: txLoading,     error: txError }     = useTransactions(year, month)
  const upsert = useUpsertBudget()

  const isLoading = budgetLoading || txLoading
  const subtitle  = `${MESES_PT[month - 1]} ${year}`
  const apiBase   = process.env.NEXT_PUBLIC_API_URL

  // Fetch alerts and projections from API
  useEffect(() => {
    if (!apiBase) return

    async function fetchBudgetData() {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        const token = session?.access_token
        if (!token) return

        const headers = { Authorization: `Bearer ${token}` }

        const [alertsRes, statusRes] = await Promise.all([
          fetch(`${apiBase}/budget/alerts`, { headers }),
          fetch(`${apiBase}/budget/status`, { headers }),
        ])

        if (alertsRes.ok) {
          const data = await alertsRes.json() as AlertBadge[]
          setAlerts(data)
        }
        if (statusRes.ok) {
          const data = await statusRes.json() as Array<{ category: string; projected_close: number }>
          setProjections(Object.fromEntries(data.map((s) => [s.category, s.projected_close])))
        }
      } catch { /* silent */ }
    }

    void fetchBudgetData()
  }, [apiBase, budgets])

  function prevMonth() {
    if (month === 1) { setMonth(12); setYear((y) => y - 1) }
    else setMonth((m) => m - 1)
  }
  function nextMonth() {
    if (month === 12) { setMonth(1); setYear((y) => y + 1) }
    else setMonth((m) => m + 1)
  }

  const spentMap: Record<string, number> = {}
  txs?.filter((t) => t.type === "GASTO").forEach((t) => {
    spentMap[t.category] = (spentMap[t.category] ?? 0) + t.amount
  })

  const totalLimit = budgets?.reduce((s, b) => s + b.monthly_limit, 0) ?? 0
  const totalSpent = budgets?.reduce((s, b) => s + (spentMap[b.category] ?? 0), 0) ?? 0

  const currentLimits = Object.fromEntries((budgets ?? []).map((b) => [b.category, b.monthly_limit]))

  async function handleCopyPrevMonth() {
    const prevM = month === 1
      ? { year: year - 1, month: 12 }
      : { year, month: month - 1 }
    const { data: prev } = await supabase
      .from("budgets")
      .select("*")
      .eq("year", prevM.year)
      .eq("month", prevM.month)
    if (!prev?.length) return
    for (const pb of prev) {
      await upsert.mutateAsync({ category: pb.category, monthly_limit: pb.monthly_limit, year, month })
    }
  }

  async function handleSaveBudget(limits: Record<string, number>) {
    for (const [category, monthly_limit] of Object.entries(limits)) {
      await upsert.mutateAsync({ category, monthly_limit, year, month })
    }
  }

  return (
    <div className="p-4 md:p-6 max-w-3xl mx-auto">
      <div className="flex items-start justify-between mb-2">
        <PageHeader title="Orçamento" />
        <div className="flex items-center gap-3 mt-1">
          {budgets && budgets.length > 0 && (
            <button
              type="button"
              onClick={handleCopyPrevMonth}
              className="text-xs text-[var(--ink-3)] hover:text-[var(--ink)] transition-colors"
              title="Copiar limites do mês anterior"
            >
              Copiar mês ant.
            </button>
          )}
          <button
            type="button"
            onClick={() => setSetupOpen(true)}
            className="text-xs text-[var(--brass)] hover:underline shrink-0"
          >
            Configurar
          </button>
        </div>
      </div>

      {/* Alert badges */}
      {alerts.length > 0 && (
        <div id="alerts-section" className="flex flex-col gap-2 mb-4">
          {alerts.map((a) => (
            <div
              key={a.category}
              className={cn(
                "px-3 py-2 rounded-md text-xs",
                a.overbudget
                  ? "bg-[var(--neg)]/10 text-[var(--neg)]"
                  : "bg-[var(--warn,#F59E0B)]/10 text-[var(--warn,#F59E0B)]",
              )}
            >
              ⚠ {a.message}
            </div>
          ))}
        </div>
      )}

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
          <EnvelopeBar pct={totalLimit > 0 ? (totalSpent / totalLimit) * 100 : 0} />
        </KCard>
      )}

      {/* Per-category budgets */}
      {isLoading ? (
        <div className="flex flex-col gap-3">
          {Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} className="h-20" />)}
        </div>
      ) : budgetError || txError ? (
        <p className="text-sm text-[var(--neg)]">
          Erro ao carregar orçamento: {((budgetError || txError) as Error).message}
        </p>
      ) : !budgets || budgets.length === 0 ? (
        <div className="flex flex-col items-center gap-4 py-12">
          <p className="text-sm text-[var(--ink-3)]">Nenhum orçamento configurado.</p>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => setSetupOpen(true)}
              className="px-4 py-2 text-sm rounded-md bg-[var(--brass)] text-[var(--bg)] font-medium hover:opacity-90"
            >
              Configurar orçamento
            </button>
            <button
              type="button"
              onClick={handleCopyPrevMonth}
              className="px-4 py-2 text-sm rounded-md border border-[var(--rule)] text-[var(--ink-3)] hover:text-[var(--ink)] transition-colors"
            >
              Copiar mês anterior
            </button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {budgets.map((b) => {
            const spent     = spentMap[b.category] ?? 0
            const pct       = b.monthly_limit > 0 ? (spent / b.monthly_limit) * 100 : 0
            const over      = spent > b.monthly_limit
            const available = b.monthly_limit - spent
            const projected = projections[b.category]

            return (
              <KCard key={b.id} variant="surface">
                {/* Envelope layout: disponível em destaque + meta */}
                <div className="flex items-start justify-between mb-2">
                  {/* Left: disponível (protagonista) */}
                  <div>
                    <p className="text-[10px] font-medium text-[var(--ink-3)] uppercase tracking-wide mb-0.5">
                      {over ? "Estouro" : "Disponível"}
                    </p>
                    <p
                      className="text-xl font-semibold tabular leading-tight"
                      style={{ color: envelopeColor(pct) }}
                    >
                      {over
                        ? `−${fmtBRL(Math.abs(available))}`
                        : fmtBRL(available)}
                    </p>
                  </div>
                  {/* Right: categoria + gasto/limite */}
                  <div className="text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <span className="text-sm font-medium text-[var(--ink)]">{b.category}</span>
                      {over && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-500/10 text-[var(--neg)] font-medium">
                          Estouro
                        </span>
                      )}
                    </div>
                    <p className="text-xs tabular text-[var(--ink-4)] mt-0.5">
                      {fmtBRL(spent)} / {fmtBRL(b.monthly_limit)}
                    </p>
                    {projected !== undefined && (
                      <p className="text-xs text-[var(--ink-4)] mt-0.5">
                        Projeção: {fmtBRL(projected)}
                      </p>
                    )}
                  </div>
                </div>
                <EnvelopeBar pct={pct} />
              </KCard>
            )
          })}
        </div>
      )}

      <BudgetSetupDialog
        open={setupOpen}
        onOpenChange={setSetupOpen}
        currentLimits={currentLimits}
        year={year}
        month={month}
        onSave={handleSaveBudget}
      />
    </div>
  )
}
