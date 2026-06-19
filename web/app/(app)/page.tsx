"use client"

import { useState, useMemo } from "react"
import { PageHeader } from "@/components/ui/page-header"
import { KpiCard } from "@/components/ui/kpi-card"
import { TxRow } from "@/components/ui/tx-row"
import { SkeletonCard, SkeletonRow } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/ui/empty-state"
import { KCard } from "@/components/ui/kcard"
import { SafeToSpendHero } from "@/components/ui/safe-to-spend"
import { UpcomingBills } from "@/components/ui/upcoming-bills"
import { NetWorthProjection } from "@/components/ui/networth-projection"
import { NetWorthChart, type NetWorthPoint } from "@/components/ui/networth-chart"
import { computeSafeToSpend } from "@/lib/finance/safe-to-spend"
import { averageMonthlyNet, projectNetWorth } from "@/lib/finance/projection"
import { useTransactions, useMonthlyTotals } from "@/lib/queries/useTransactions"
import { useBankAccounts } from "@/lib/queries/useAccounts"
import { useInvestments } from "@/lib/queries/useInvestments"
import { fmtBRL } from "@/lib/utils"
import { CAT_COLORS } from "@/lib/tx-schema"
import Link from "next/link"
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts"

const MESES_PT = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

function computeNetWorthHistory(
  currentCash: number,
  currentInvestments: number,
  allTxs: { date: string; amount: number; type: string }[],
  months = 12,
): NetWorthPoint[] {
  const now    = new Date()
  const result: NetWorthPoint[] = []

  for (let i = months - 1; i >= 0; i--) {
    const d        = new Date(now.getFullYear(), now.getMonth() - i, 1)
    const monthKey = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`
    const label    = d.toLocaleDateString("pt-BR", { month: "short", year: "2-digit" })
      .replace(".", "")
      .replace(/^(.)/, c => c.toUpperCase())

    // Net transactions recorded AFTER this month (moves balance forward in time)
    const netAfter = allTxs
      .filter(t => t.date.slice(0, 7) > monthKey)
      .reduce((s, t) => s + (t.type === "GANHO" ? t.amount : -t.amount), 0)

    const caixa = Math.max(0, currentCash - netAfter)
    result.push({ month: label, total: caixa + currentInvestments, caixa })
  }

  return result
}

function aggregateByMonth(txs: { date: string; amount: number; type: string }[]) {
  const map: Record<string, { ganhos: number; gastos: number }> = {}
  for (const tx of txs) {
    const k = tx.date.slice(0, 7)
    if (!map[k]) map[k] = { ganhos: 0, gastos: 0 }
    if (tx.type === "GANHO") map[k].ganhos += tx.amount
    else if (tx.type === "GASTO") map[k].gastos += tx.amount
  }
  return map
}

export default function HomePage() {
  const now = new Date()
  const [year, setYear]   = useState(now.getFullYear())
  const [month, setMonth] = useState(now.getMonth() + 1)

  const isCurrentMonth = year === now.getFullYear() && month === now.getMonth() + 1

  function prevMonth() {
    if (month === 1) { setYear(y => y - 1); setMonth(12) }
    else              setMonth(m => m - 1)
  }
  function nextMonth() {
    if (isCurrentMonth) return
    if (month === 12) { setYear(y => y + 1); setMonth(1) }
    else               setMonth(m => m + 1)
  }

  const { data: txs, isLoading: txLoading, error: txError } = useTransactions(year, month)
  const { data: accounts, isLoading: accLoading } = useBankAccounts()
  const { data: investments } = useInvestments()
  const { data: history } = useMonthlyTotals(year, 12)

  const ganhos   = txs?.filter(t => t.type === "GANHO").reduce((s, t) => s + t.amount, 0) ?? 0
  const gastos   = txs?.filter(t => t.type === "GASTO").reduce((s, t) => s + t.amount, 0) ?? 0
  const poupanca = ganhos > 0 ? ((ganhos - gastos) / ganhos) * 100 : 0
  const safe     = computeSafeToSpend(accounts ?? [], txs ?? [])

  const investido    = investments?.reduce((s, i) => s + i.quantity * i.current_price, 0) ?? 0
  const patrimonio   = safe.caixa + investido
  const aporteMensal = averageMonthlyNet(history ?? [])
  const projection   = projectNetWorth(patrimonio, aporteMensal, 12)

  // Net Worth History (synthetic from transactions + current balances)
  const nwHistory = useMemo(
    () => computeNetWorthHistory(safe.caixa, investido, history ?? []),
    [safe.caixa, investido, history],
  )

  // Monthly aggregates for deltas and sparkline
  const agg = useMemo(() => aggregateByMonth(history ?? []), [history])

  const currKey = `${year}-${String(month).padStart(2, "0")}`
  const prevDate = month === 1
    ? { year: year - 1, month: 12 }
    : { year, month: month - 1 }
  const prevKey = `${prevDate.year}-${String(prevDate.month).padStart(2, "0")}`

  const prevAgg     = agg[prevKey] ?? { ganhos: 0, gastos: 0 }
  const deltaGanhos = prevAgg.ganhos > 0
    ? ((ganhos - prevAgg.ganhos) / prevAgg.ganhos) * 100
    : undefined
  const deltaGastos = prevAgg.gastos > 0
    ? ((gastos - prevAgg.gastos) / prevAgg.gastos) * 100
    : undefined

  // Sparkline: 6 months of net ending at current month
  const sparklineNet = useMemo(() => Array.from({ length: 6 }, (_, i) => {
    const d = new Date(year, month - 1 - (5 - i), 1)
    const k = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`
    const m = agg[k] ?? { ganhos: 0, gastos: 0 }
    return m.ganhos - m.gastos
  }), [agg, year, month])

  // Category breakdown for pie chart
  const catMap: Record<string, number> = {}
  txs?.filter(t => t.type === "GASTO").forEach(t => {
    catMap[t.category] = (catMap[t.category] ?? 0) + t.amount
  })
  const pieData = Object.entries(catMap)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)

  const recentTxs = txs?.slice(0, 5) ?? []
  const isLoading = txLoading || accLoading

  // Month navigation subtitle
  const monthNav = (
    <div className="flex items-center gap-2 text-[var(--ink-3)]">
      <button
        type="button"
        onClick={prevMonth}
        className="w-5 h-5 flex items-center justify-center rounded hover:text-[var(--ink)] hover:bg-[var(--surface)] transition-colors"
        aria-label="Mês anterior"
      >
        ‹
      </button>
      <span className="text-sm font-medium min-w-[72px] text-center">
        {MESES_PT[month - 1]} {year}
      </span>
      <button
        type="button"
        onClick={nextMonth}
        disabled={isCurrentMonth}
        className="w-5 h-5 flex items-center justify-center rounded hover:text-[var(--ink)] hover:bg-[var(--surface)] transition-colors disabled:opacity-30 disabled:cursor-default"
        aria-label="Próximo mês"
      >
        ›
      </button>
    </div>
  )

  return (
    <div className="p-4 md:p-6 max-w-5xl mx-auto">
      <PageHeader
        title="Dashboard"
        subtitle={monthNav as unknown as string}
        action={
          <Link
            href="/transacoes/novo"
            className="text-xs px-3 py-1.5 rounded-md bg-[var(--brass)] text-[var(--bg)] font-medium hover:opacity-90 transition-opacity"
          >
            + Lançamento
          </Link>
        }
      />

      {isLoading ? (
        <>
          <SkeletonCard className="mb-4 h-32" />
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
            {Array.from({ length: 3 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        </>
      ) : txError ? (
        <EmptyState
          icon="⚠"
          title="Erro ao carregar dados"
          description="Verifique se as migrations Fase 0 foram aplicadas e tente novamente."
        />
      ) : (
        <>
          {/* 1. Patrimônio histórico — hero visual do dashboard */}
          {nwHistory.length >= 2 && (
            <KCard className="mb-4 overflow-hidden">
              <div className="flex items-end justify-between mb-1">
                <div>
                  <p className="text-xs font-medium text-[var(--ink-3)] uppercase tracking-wide">
                    Patrimônio Líquido
                  </p>
                  <p className="text-2xl font-semibold text-[var(--brass)] tabular leading-tight">
                    {fmtBRL(patrimonio)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-[var(--ink-4)]">12 meses</p>
                </div>
              </div>
              <NetWorthChart points={nwHistory} />
            </KCard>
          )}

          {/* 2. Estado real: o que sobra depois das contas */}
          <SafeToSpendHero data={safe} />

          {/* 3. O que ameaça esse número */}
          <UpcomingBills bills={safe.upcoming} />

          {/* 4. KPIs com delta vs mês anterior + sparkline de saldo */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
            <KpiCard
              label="Entradas · mês"
              value={ganhos}
              format="brl"
              accent
              delta={deltaGanhos}
              sparkline={sparklineNet}
            />
            <KpiCard
              label="Saídas · mês"
              value={gastos}
              format="brl"
              delta={deltaGastos}
            />
            <KpiCard
              label="Taxa de poupança"
              value={poupanca}
              format="pct"
            />
          </div>

          {/* 5. Para onde isso vai — projeção de patrimônio */}
          {patrimonio > 0 && (
            <NetWorthProjection points={projection} current={patrimonio} monthlyNet={aporteMensal} />
          )}
        </>
      )}

      {/* Donut — gastos por categoria */}
      {!isLoading && !txError && txs && txs.length > 0 && (
        <div className="mb-6">
          <KCard>
            <p className="text-xs font-medium text-[var(--ink-3)] uppercase tracking-wide mb-3">
              Gastos por categoria
            </p>
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    dataKey="value"
                    nameKey="name"
                  >
                    {pieData.map((entry) => (
                      <Cell
                        key={entry.name}
                        fill={CAT_COLORS[entry.name] ?? "#64748B"}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(v) => typeof v === "number" ? fmtBRL(v) : v}
                    contentStyle={{
                      background: "var(--card)",
                      border: "1px solid var(--rule)",
                      borderRadius: "6px",
                      fontSize: "12px",
                      color: "var(--ink)",
                    }}
                  />
                  <Legend
                    iconSize={8}
                    wrapperStyle={{ fontSize: "11px", color: "var(--ink-3)" }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-xs text-[var(--ink-4)] py-8 text-center">
                Sem gastos registrados este mês.
              </p>
            )}
          </KCard>
        </div>
      )}

      {/* Últimas transações */}
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-xs font-medium text-[var(--ink-3)] uppercase tracking-wide">
          Últimas transações
        </h2>
        <Link href="/transacoes" className="text-xs text-[var(--brass)] hover:opacity-80">
          Ver todas →
        </Link>
      </div>

      <KCard padding="none">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonRow key={i} />)
        ) : recentTxs.length > 0 ? (
          <div className="divide-y divide-[var(--rule)]">
            {recentTxs.map((tx) => (
              <TxRow key={tx.id} tx={tx} />
            ))}
          </div>
        ) : (
          <EmptyState
            title="Nenhuma transação este mês"
            action={
              <Link
                href="/transacoes/novo"
                className="text-xs px-3 py-1.5 rounded-md bg-[var(--brass)] text-[var(--bg)] font-medium"
              >
                + Primeiro lançamento
              </Link>
            }
          />
        )}
      </KCard>
    </div>
  )
}
