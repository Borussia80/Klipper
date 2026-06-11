"use client"

import { PageHeader } from "@/components/ui/page-header"
import { KCard } from "@/components/ui/kcard"
import { KpiCard } from "@/components/ui/kpi-card"
import { SkeletonCard, SkeletonRow } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/ui/empty-state"
import { useInvestments } from "@/lib/queries/useInvestments"
import { fmtBRL, fmtPct } from "@/lib/utils"
import { cn } from "@/lib/utils"

const TYPE_COLOR: Record<string, string> = {
  FII:          "var(--brass)",
  Ação:         "#3B82F6",
  "Renda Fixa": "var(--pos)",
  Caixa:        "var(--ink-3)",
}

export default function InvestimentosPage() {
  const { data: positions, isLoading, error } = useInvestments()

  const totalValue    = positions?.reduce((s, p) => s + p.quantity * p.current_price, 0) ?? 0
  const totalCost     = positions?.reduce((s, p) => s + p.quantity * p.avg_price, 0) ?? 0
  const totalGain     = totalValue - totalCost
  const totalGainPct  = totalCost > 0 ? (totalGain / totalCost) * 100 : 0
  const avgDY         = positions?.length
    ? positions.reduce((s, p) => s + p.dy_12m, 0) / positions.length
    : 0

  // Group by type
  const byType: Record<string, { value: number; count: number }> = {}
  positions?.forEach(p => {
    const v = p.quantity * p.current_price
    if (!byType[p.type]) byType[p.type] = { value: 0, count: 0 }
    byType[p.type].value += v
    byType[p.type].count++
  })

  return (
    <div className="p-4 md:p-6 max-w-5xl mx-auto">
      <PageHeader title="Investimentos" subtitle="Carteira atual" />

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : error ? (
          <div className="col-span-4">
            <EmptyState icon="⚠" title="Erro ao carregar carteira" description="Verifique as migrations Fase 0." />
          </div>
        ) : (
          <>
            <KpiCard label="Patrimônio" value={totalValue} format="brl" accent />
            <KpiCard label="Ganho / Perda" value={totalGain} format="brl"
              delta={totalGainPct} deltaLabel="sobre custo" />
            <KpiCard label="DY médio 12m" value={avgDY} format="pct" />
            <KpiCard label="Posições" value={positions?.length ?? 0} format="number" />
          </>
        )}
      </div>

      {/* Alocação por tipo */}
      {!isLoading && !error && Object.keys(byType).length > 0 && (
        <KCard className="mb-6">
          <p className="text-xs font-medium text-[var(--ink-3)] uppercase tracking-wide mb-3">
            Alocação por tipo
          </p>
          <div className="flex flex-col gap-2">
            {Object.entries(byType)
              .sort(([, a], [, b]) => b.value - a.value)
              .map(([type, { value, count }]) => {
                const pct = totalValue > 0 ? (value / totalValue) * 100 : 0
                return (
                  <div key={type} className="flex items-center gap-3">
                    <span
                      className="w-2.5 h-2.5 rounded-sm shrink-0"
                      style={{ background: TYPE_COLOR[type] ?? "var(--ink-4)" }}
                    />
                    <span className="text-sm text-[var(--ink)] w-24 shrink-0">{type}</span>
                    <div className="flex-1 h-1.5 rounded-full bg-[var(--layer)]">
                      <div
                        className="h-full rounded-full"
                        style={{ width: `${pct}%`, background: TYPE_COLOR[type] ?? "var(--ink-4)" }}
                      />
                    </div>
                    <span className="text-xs tabular text-[var(--ink-3)] w-10 text-right">{pct.toFixed(0)}%</span>
                    <span className="text-xs tabular text-[var(--ink)] w-28 text-right">{fmtBRL(value)}</span>
                    <span className="text-xs text-[var(--ink-4)] w-16 text-right">{count} pos.</span>
                  </div>
                )
              })}
          </div>
        </KCard>
      )}

      {/* Posições */}
      <p className="text-xs font-medium text-[var(--ink-3)] uppercase tracking-wide mb-3">
        Posições
      </p>
      <KCard padding="none">
        {isLoading ? (
          Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
        ) : !positions || positions.length === 0 ? (
          <EmptyState
            title="Carteira vazia"
            description="Adicione posições pelo app Streamlit (Investimentos → Posições)."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--rule)]">
                  {["Ticker", "Tipo", "Qtd", "PM", "Atual", "Valor", "G/P", "%"].map(h => (
                    <th key={h} className="px-4 py-2 text-left text-xs font-medium text-[var(--ink-4)] uppercase tracking-wide">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {positions.map((p) => {
                  const value   = p.quantity * p.current_price
                  const gain    = p.quantity * (p.current_price - p.avg_price)
                  const gainPct = p.avg_price > 0 ? (p.current_price / p.avg_price - 1) * 100 : 0
                  const up      = gain >= 0
                  return (
                    <tr key={p.id} className="border-b border-[var(--rule)] last:border-0 hover:bg-[var(--surface)] transition-colors">
                      <td className="px-4 py-3 font-semibold text-[var(--brass)]">{p.ticker}</td>
                      <td className="px-4 py-3">
                        <span className="text-xs px-2 py-0.5 rounded bg-[var(--layer)] text-[var(--ink-3)]">{p.type}</span>
                      </td>
                      <td className="px-4 py-3 tabular text-[var(--ink-3)]">{p.quantity}</td>
                      <td className="px-4 py-3 tabular text-[var(--ink-3)]">{fmtBRL(p.avg_price)}</td>
                      <td className="px-4 py-3 tabular text-[var(--ink)]">{fmtBRL(p.current_price)}</td>
                      <td className="px-4 py-3 tabular text-[var(--ink)] font-medium">{fmtBRL(value)}</td>
                      <td className={cn("px-4 py-3 tabular", up ? "text-[var(--pos)]" : "text-[var(--neg)]")}>
                        {up ? "+" : ""}{fmtBRL(gain)}
                      </td>
                      <td className={cn("px-4 py-3 tabular", up ? "text-[var(--pos)]" : "text-[var(--neg)]")}>
                        {fmtPct(gainPct)}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </KCard>
    </div>
  )
}
