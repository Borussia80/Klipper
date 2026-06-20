"use client"

import { useState } from "react"
import * as Dialog from "@radix-ui/react-dialog"
import { PageHeader } from "@/components/ui/page-header"
import { KCard } from "@/components/ui/kcard"
import { KpiCard } from "@/components/ui/kpi-card"
import { SkeletonCard, SkeletonRow } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/ui/empty-state"
import { InvestmentDialog } from "@/components/ui/investment-dialog"
import { useInvestments, useDeleteInvestment, type Investment } from "@/lib/queries/useInvestments"
import { useM1Score, useFragility, useRunAnalysis } from "@/lib/queries/useEngines"
import { fmtBRL, fmtPct } from "@/lib/utils"
import { cn } from "@/lib/utils"
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts"

const TYPE_COLOR: Record<string, string> = {
  FII:          "var(--brass)",
  Ação:         "#3B82F6",
  "Renda Fixa": "var(--pos)",
  Caixa:        "var(--ink-3)",
}

const FRAGILITY_BADGE: Record<string, string> = {
  low:    "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
  medium: "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400",
  high:   "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
}

const LEVEL_LABEL: Record<string, string> = { low: "Baixa", medium: "Média", high: "Alta" }

function fragilityLevel(score: number): "low" | "medium" | "high" {
  if (score < 0.3) return "low"
  if (score < 0.6) return "medium"
  return "high"
}

function M1ScoreCell({ ticker }: { ticker: string }) {
  const { data, isFetching } = useM1Score(ticker)
  if (isFetching) return <span className="text-[var(--ink-4)] animate-pulse">…</span>
  if (!data) return <span className="text-[var(--ink-4)]">—</span>
  const score = data.score as number
  const level = fragilityLevel(1 - score)
  return (
    <span className={cn("text-xs px-1.5 py-0.5 rounded font-medium", FRAGILITY_BADGE[level])}>
      {score.toFixed(2)}
    </span>
  )
}

function FragilityCell({
  ticker, byTicker,
}: { ticker: string; byTicker: { ticker: string; score: number }[] }) {
  const entry = byTicker.find((e) => e.ticker === ticker)
  if (!entry) return <span className="text-[var(--ink-4)]">—</span>
  const level = fragilityLevel(entry.score)
  return (
    <span className={cn("text-xs px-1.5 py-0.5 rounded font-medium", FRAGILITY_BADGE[level])}>
      {LEVEL_LABEL[level]}
    </span>
  )
}

function KebabMenu({ onEdit, onDelete }: { onEdit: () => void; onDelete: () => void }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="p-1 rounded text-[var(--ink-4)] hover:text-[var(--ink)] transition-colors"
        aria-label="Opções"
      >
        ⋮
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-6 z-20 min-w-[120px] rounded-md bg-[var(--card)] border border-[var(--rule)] shadow-lg py-1">
            <button
              type="button"
              className="w-full px-3 py-1.5 text-sm text-left text-[var(--ink)] hover:bg-[var(--surface)]"
              onClick={() => { setOpen(false); onEdit() }}
            >
              Editar
            </button>
            <button
              type="button"
              className="w-full px-3 py-1.5 text-sm text-left text-[var(--neg)] hover:bg-[var(--surface)]"
              onClick={() => { setOpen(false); onDelete() }}
            >
              Excluir
            </button>
          </div>
        </>
      )}
    </div>
  )
}

function DeleteConfirmDialog({
  open, onOpenChange, ticker, onConfirm,
}: {
  open: boolean; onOpenChange: (open: boolean) => void; ticker: string; onConfirm: () => void
}) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/60 z-40" />
        <Dialog.Content
          className="fixed left-1/2 top-1/2 z-50 w-full max-w-sm -translate-x-1/2 -translate-y-1/2 rounded-xl bg-[var(--card)] border border-[var(--rule)] p-6 shadow-xl focus:outline-none"
          aria-describedby="delete-inv-desc"
        >
          <Dialog.Title className="text-base font-semibold text-[var(--ink)] mb-2">
            Excluir {ticker}?
          </Dialog.Title>
          <p id="delete-inv-desc" className="text-sm text-[var(--ink-3)] mb-5">
            Esta ação é permanente e removerá o ativo da carteira.
          </p>
          <div className="flex gap-2">
            <Dialog.Close asChild>
              <button type="button" className="flex-1 py-2 text-sm rounded-md border border-[var(--rule)] text-[var(--ink-3)] hover:text-[var(--ink)]">
                Cancelar
              </button>
            </Dialog.Close>
            <button
              type="button"
              className="flex-1 py-2 text-sm rounded-md bg-[var(--neg)] text-white font-medium hover:opacity-90"
              onClick={onConfirm}
            >
              Excluir
            </button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

export default function InvestimentosPage() {
  const { data: positions, isLoading, error } = useInvestments()
  const deleteInvestment = useDeleteInvestment()
  const { data: fragilityData } = useFragility()
  const runAnalysis = useRunAnalysis()

  const [dialogOpen, setDialogOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<Investment | undefined>()
  const [deleteTarget, setDeleteTarget] = useState<Investment | undefined>()
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const byTicker: { ticker: string; score: number }[] = fragilityData?.by_ticker ?? []

  const totalValue   = positions?.reduce((s, p) => s + p.quantity * p.current_price, 0) ?? 0
  const totalCost    = positions?.reduce((s, p) => s + p.quantity * p.avg_price, 0) ?? 0
  const totalGain    = totalValue - totalCost
  const totalGainPct = totalCost > 0 ? (totalGain / totalCost) * 100 : 0
  const projDY       = positions?.reduce(
    (s, p) => s + (p.dy_12m / 100) * p.quantity * p.current_price, 0,
  ) ?? 0

  const projDYpct    = totalValue > 0 ? (projDY / totalValue) * 100 : 0

  const byType: Record<string, { value: number; count: number }> = {}
  positions?.forEach((p) => {
    const v = p.quantity * p.current_price
    if (!byType[p.type]) byType[p.type] = { value: 0, count: 0 }
    byType[p.type].value += v
    byType[p.type].count++
  })

  const pieDataByType = Object.entries(byType)
    .sort(([, a], [, b]) => b.value - a.value)
    .map(([name, { value, count }]) => ({
      name, value, count,
      pct: totalValue > 0 ? (value / totalValue) * 100 : 0,
    }))

  async function handleAnalyze() {
    setIsAnalyzing(true)
    await runAnalysis()
    setIsAnalyzing(false)
  }

  function openNew() {
    setEditTarget(undefined)
    setDialogOpen(true)
  }

  function openEdit(inv: Investment) {
    setEditTarget(inv)
    setDialogOpen(true)
  }

  return (
    <div className="p-4 md:p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-1">
        <PageHeader title="Investimentos" subtitle="Carteira atual" />
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="px-3 py-1.5 text-sm rounded-md border border-[var(--brass)] text-[var(--brass)] hover:bg-[var(--brass)] hover:text-[var(--bg)] transition-colors disabled:opacity-50"
          >
            {isAnalyzing ? "Analisando…" : "Analisar carteira"}
          </button>
          <button
            type="button"
            onClick={openNew}
            className="px-3 py-1.5 text-sm rounded-md bg-[var(--brass)] text-[var(--bg)] font-medium hover:opacity-90"
          >
            + Novo ativo
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6 mt-4">
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
            <KpiCard label="DY projetado/ano" value={projDY} format="brl" />
            <KpiCard label="DY % patrimônio" value={projDYpct} format="pct" />
          </>
        )}
      </div>

      {/* Alocação por tipo */}
      {!isLoading && !error && pieDataByType.length > 0 && (
        <KCard className="mb-6">
          <p className="text-xs font-medium text-[var(--ink-3)] uppercase tracking-wide mb-4">
            Alocação por tipo
          </p>
          <div className="flex flex-col md:flex-row items-center gap-6">
            {/* Donut */}
            <div className="shrink-0">
              <ResponsiveContainer width={180} height={180}>
                <PieChart>
                  <Pie
                    data={pieDataByType}
                    cx="50%"
                    cy="50%"
                    innerRadius={52}
                    outerRadius={80}
                    dataKey="value"
                    nameKey="name"
                    strokeWidth={0}
                  >
                    {pieDataByType.map((entry) => (
                      <Cell key={entry.name} fill={TYPE_COLOR[entry.name] ?? "#94A3B8"} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(v) => fmtBRL(v as number)}
                    contentStyle={{
                      background: "var(--card)",
                      border: "1px solid var(--rule)",
                      borderRadius: "6px",
                      fontSize: "11px",
                      color: "var(--ink)",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            {/* Bars + values */}
            <div className="flex-1 w-full flex flex-col gap-2.5">
              {pieDataByType.map(({ name, value, pct, count }) => (
                <div key={name} className="flex items-center gap-3">
                  <span
                    className="w-2.5 h-2.5 rounded-sm shrink-0"
                    style={{ background: TYPE_COLOR[name] ?? "#94A3B8" }}
                  />
                  <span className="text-xs text-[var(--ink-3)] w-24 shrink-0">{name}</span>
                  <div className="flex-1 h-1.5 rounded-full bg-[var(--layer)]">
                    <div
                      className="h-full rounded-full transition-all duration-300"
                      style={{ width: `${pct}%`, background: TYPE_COLOR[name] ?? "#94A3B8" }}
                    />
                  </div>
                  <span className="text-xs tabular text-[var(--ink-3)] w-9 text-right">
                    {pct.toFixed(0)}%
                  </span>
                  <span className="text-xs tabular text-[var(--ink)] w-28 text-right">
                    {fmtBRL(value)}
                  </span>
                  <span className="text-xs text-[var(--ink-4)] w-14 text-right">
                    {count} pos.
                  </span>
                </div>
              ))}
            </div>
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
            description="Clique em '+ Novo ativo' para cadastrar posições."
          />
        ) : (
          <>
            {/* Mobile cards */}
            <div className="md:hidden divide-y divide-[var(--rule)]">
              {positions.map((p) => {
                const value   = p.quantity * p.current_price
                const gain    = p.quantity * (p.current_price - p.avg_price)
                const gainPct = p.avg_price > 0 ? (p.current_price / p.avg_price - 1) * 100 : 0
                const up      = gain >= 0
                const color   = TYPE_COLOR[p.type] ?? "#94A3B8"
                return (
                  <div key={p.id} className="flex items-center gap-3 px-4 py-3">
                    {/* Icon */}
                    <div
                      className="shrink-0 w-9 h-9 rounded-full flex items-center justify-center text-[10px] font-bold"
                      style={{ backgroundColor: color + "22" }}
                    >
                      <span style={{ color }}>{p.ticker.slice(0, 4)}</span>
                    </div>
                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-baseline gap-1.5">
                        <span className="text-sm font-semibold text-[var(--brass)]">{p.ticker}</span>
                        <span className="text-[10px] text-[var(--ink-4)]">{p.type}</span>
                      </div>
                      <p className="text-xs text-[var(--ink-4)] tabular">
                        {p.quantity} × {fmtBRL(p.current_price)}
                      </p>
                    </div>
                    {/* Value + gain */}
                    <div className="text-right shrink-0">
                      <p className="text-sm font-semibold text-[var(--ink)] tabular">{fmtBRL(value)}</p>
                      <p className={cn("text-xs tabular", up ? "text-[var(--pos)]" : "text-[var(--neg)]")}>
                        {up ? "+" : ""}{fmtPct(gainPct)}
                      </p>
                    </div>
                    <KebabMenu onEdit={() => openEdit(p)} onDelete={() => setDeleteTarget(p)} />
                  </div>
                )
              })}
            </div>
            {/* Desktop table */}
            <div className="hidden md:block overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--rule)]">
                  {["Ticker", "Tipo", "Qtd", "PM", "Atual", "Valor", "G/P", "%", "M1", "Fragilidade", ""].map((h) => (
                    <th key={h} className="px-3 py-2 text-left text-xs font-medium text-[var(--ink-4)] uppercase tracking-wide">
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
                      <td className="px-3 py-3 font-semibold text-[var(--brass)]">{p.ticker}</td>
                      <td className="px-3 py-3">
                        <span className="text-xs px-2 py-0.5 rounded bg-[var(--layer)] text-[var(--ink-3)]">{p.type}</span>
                      </td>
                      <td className="px-3 py-3 tabular text-[var(--ink-3)]">{p.quantity}</td>
                      <td className="px-3 py-3 tabular text-[var(--ink-3)]">{fmtBRL(p.avg_price)}</td>
                      <td className="px-3 py-3 tabular text-[var(--ink)]">{fmtBRL(p.current_price)}</td>
                      <td className="px-3 py-3 tabular text-[var(--ink)] font-medium">{fmtBRL(value)}</td>
                      <td className={cn("px-3 py-3 tabular", up ? "text-[var(--pos)]" : "text-[var(--neg)]")}>
                        {up ? "+" : ""}{fmtBRL(gain)}
                      </td>
                      <td className={cn("px-3 py-3 tabular", up ? "text-[var(--pos)]" : "text-[var(--neg)]")}>
                        {fmtPct(gainPct)}
                      </td>
                      <td className="px-3 py-3">
                        <M1ScoreCell ticker={p.ticker} />
                      </td>
                      <td className="px-3 py-3">
                        <FragilityCell ticker={p.ticker} byTicker={byTicker} />
                      </td>
                      <td className="px-3 py-3">
                        <KebabMenu
                          onEdit={() => openEdit(p)}
                          onDelete={() => setDeleteTarget(p)}
                        />
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
            </div>
          </>
        )}
      </KCard>

      <InvestmentDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        initial={editTarget}
        key={editTarget?.id ?? "new"}
      />

      {deleteTarget && (
        <DeleteConfirmDialog
          open={!!deleteTarget}
          onOpenChange={(o) => { if (!o) setDeleteTarget(undefined) }}
          ticker={deleteTarget.ticker}
          onConfirm={async () => {
            await deleteInvestment.mutateAsync(deleteTarget.id)
            setDeleteTarget(undefined)
          }}
        />
      )}
    </div>
  )
}
