"use client"

import { useState } from "react"
import { PageHeader } from "@/components/ui/page-header"
import { TxRow } from "@/components/ui/tx-row"
import { SkeletonRow } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/ui/empty-state"
import { KCard } from "@/components/ui/kcard"
import { TxDialog } from "@/components/ui/tx-dialog"
import {
  useTransactions,
  useCreateTransaction,
  useDeleteTransaction,
  useUpdateTransaction,
} from "@/lib/queries/useTransactions"
import { fmtBRL } from "@/lib/utils"
import { cn } from "@/lib/utils"
import type { TxFormValues } from "@/lib/tx-schema"
import type { Database } from "@/types/database"
import Link from "next/link"

type Transaction = Database["public"]["Tables"]["transactions"]["Row"]
type TxType = "GASTO" | "GANHO" | "TODOS"

const MESES_PT = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

function parseDateLocal(dateStr: string): Date {
  const [y, m, d] = dateStr.split("-").map(Number)
  return new Date(y, m - 1, d)
}

function formatDateLabel(dateStr: string): string {
  const today = new Date(); today.setHours(0, 0, 0, 0)
  const d     = parseDateLocal(dateStr)
  const diff  = Math.round((today.getTime() - d.getTime()) / 86400000)
  if (diff === 0) return "Hoje"
  if (diff === 1) return "Ontem"
  return d.toLocaleDateString("pt-BR", { day: "numeric", month: "short" })
}

function groupByDate(txs: Transaction[]): { date: string; txs: Transaction[] }[] {
  const map = new Map<string, Transaction[]>()
  for (const tx of txs) {
    const group = map.get(tx.date) ?? []
    group.push(tx)
    map.set(tx.date, group)
  }
  return Array.from(map.entries())
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([date, txs]) => ({ date, txs }))
}

function useNow() {
  const now = new Date()
  return { year: now.getFullYear(), month: now.getMonth() + 1 }
}

export default function TransacoesPage() {
  const { year: initYear, month: initMonth } = useNow()
  const [year, setYear] = useState(initYear)
  const [month, setMonth] = useState(initMonth)
  const [typeFilter, setTypeFilter] = useState<TxType>("TODOS")
  const [search, setSearch] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Transaction | null>(null)
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null)

  const { data: txs, isLoading, error } = useTransactions(year, month)
  const createTx = useCreateTransaction()
  const updateTx = useUpdateTransaction()
  const deleteTx = useDeleteTransaction()

  function prevMonth() {
    if (month === 1) { setMonth(12); setYear(y => y - 1) }
    else setMonth(m => m - 1)
  }
  function nextMonth() {
    if (month === 12) { setMonth(1); setYear(y => y + 1) }
    else setMonth(m => m + 1)
  }

  const filtered = (txs ?? []).filter(t => {
    if (typeFilter !== "TODOS" && t.type !== typeFilter) return false
    if (search && !t.notes?.toLowerCase().includes(search.toLowerCase()) &&
        !t.category.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  const ganhos = filtered.filter(t => t.type === "GANHO").reduce((s, t) => s + t.amount, 0)
  const gastos = filtered.filter(t => t.type === "GASTO").reduce((s, t) => s + t.amount, 0)

  async function handleSubmit(values: TxFormValues) {
    if (editing) {
      await updateTx.mutateAsync({ id: editing.id, ...values })
    } else {
      await createTx.mutateAsync(values as Parameters<typeof createTx.mutateAsync>[0])
    }
    setEditing(null)
  }

  function openEdit(tx: Transaction) {
    setEditing(tx)
    setDialogOpen(true)
  }

  async function handleDelete(id: string) {
    await deleteTx.mutateAsync(id)
    setConfirmDelete(null)
  }

  const subtitle = `${MESES_PT[month - 1]} ${year}`

  return (
    <div className="p-4 md:p-6 max-w-3xl mx-auto">
      <PageHeader
        title="Transações"
        action={
          <button
            onClick={() => { setEditing(null); setDialogOpen(true) }}
            className="text-xs px-3 py-1.5 rounded-md bg-[var(--brass)] text-[var(--bg)] font-medium hover:opacity-90"
          >
            + Novo
          </button>
        }
      />

      {/* Month nav */}
      <div className="flex items-center gap-2 mb-4">
        <button onClick={prevMonth} className="p-1 rounded hover:bg-[var(--layer)] text-[var(--ink-3)]">‹</button>
        <span className="text-sm font-medium text-[var(--ink)] min-w-[80px] text-center">{subtitle}</span>
        <button onClick={nextMonth} className="p-1 rounded hover:bg-[var(--layer)] text-[var(--ink-3)]">›</button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2 mb-4">
        {(["TODOS", "GASTO", "GANHO"] as TxType[]).map((t) => (
          <button
            key={t}
            onClick={() => setTypeFilter(t)}
            className={cn(
              "text-xs px-3 py-1 rounded-full border transition-colors",
              typeFilter === t
                ? "bg-[var(--brass)] text-[var(--bg)] border-[var(--brass)]"
                : "border-[var(--rule)] text-[var(--ink-3)] hover:border-[var(--ink-4)]"
            )}
          >
            {t === "TODOS" ? "Todos" : t === "GASTO" ? "Saídas" : "Entradas"}
          </button>
        ))}
        <input
          type="search"
          placeholder="Buscar…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="ml-auto text-xs px-3 py-1 rounded-full border border-[var(--rule)] bg-[var(--surface)] text-[var(--ink)] placeholder:text-[var(--ink-4)] focus:outline-none focus:ring-1 focus:ring-[var(--brass)] w-36"
        />
      </div>

      {/* Summary row */}
      {!isLoading && !error && (
        <div className="flex gap-4 mb-4 text-xs text-[var(--ink-3)]">
          <span><span className="text-[var(--pos)] font-medium">{fmtBRL(ganhos)}</span> entradas</span>
          <span><span className="text-[var(--ink)] font-medium">{fmtBRL(gastos)}</span> saídas</span>
          <span className="ml-auto">{filtered.length} transações</span>
        </div>
      )}

      {/* List */}
      <KCard padding="none">
        {isLoading ? (
          Array.from({ length: 6 }).map((_, i) => <SkeletonRow key={i} />)
        ) : error ? (
          <EmptyState icon="⚠" title="Erro ao carregar transações" description="Verifique as migrations da Fase 0." />
        ) : filtered.length === 0 ? (
          <EmptyState
            title="Nenhuma transação"
            description={search || typeFilter !== "TODOS" ? "Tente ajustar os filtros." : `Sem lançamentos em ${subtitle}.`}
            action={
              !search && typeFilter === "TODOS" ? (
                <button
                  onClick={() => { setEditing(null); setDialogOpen(true) }}
                  className="text-xs px-3 py-1.5 rounded-md bg-[var(--brass)] text-[var(--bg)] font-medium"
                >
                  + Lançar
                </button>
              ) : undefined
            }
          />
        ) : (
          <div>
            {groupByDate(filtered).map(({ date, txs: dayTxs }) => {
              const dayGanhos = dayTxs
                .filter(t => t.type === "GANHO")
                .reduce((s, t) => s + t.amount, 0)
              const dayGastos = dayTxs
                .filter(t => t.type === "GASTO")
                .reduce((s, t) => s + t.amount, 0)
              const dayNet = dayGanhos - dayGastos
              return (
                <div key={date}>
                  {/* Date separator with daily net */}
                  <div className="flex items-center justify-between px-4 py-2 bg-[var(--surface)] border-b border-[var(--rule)]">
                    <span className="text-xs font-semibold text-[var(--ink-3)] uppercase tracking-wide">
                      {formatDateLabel(date)}
                    </span>
                    <span className={cn(
                      "text-xs font-medium tabular",
                      dayNet > 0 ? "text-[var(--pos)]" : "text-[var(--ink-3)]",
                    )}>
                      {dayNet >= 0 ? "+" : "−"}{fmtBRL(Math.abs(dayNet))}
                    </span>
                  </div>
                  {/* Transactions for the day */}
                  {dayTxs.map((tx, i) => (
                    <TxRow
                      key={tx.id}
                      tx={tx}
                      onClick={() => openEdit(tx)}
                      onDelete={() => setConfirmDelete(tx.id)}
                      className={i < dayTxs.length - 1 ? "border-b border-[var(--rule)]" : ""}
                    />
                  ))}
                </div>
              )
            })}
          </div>
        )}
      </KCard>

      {/* Confirm delete dialog */}
      {confirmDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="bg-[var(--card)] border border-[var(--rule)] rounded-xl p-6 max-w-sm w-full mx-4 shadow-xl">
            <p className="text-sm text-[var(--ink)] mb-4">Excluir esta transação?</p>
            <div className="flex gap-2">
              <button
                onClick={() => setConfirmDelete(null)}
                className="flex-1 py-2 text-sm rounded-md border border-[var(--rule)] text-[var(--ink-3)]"
              >
                Cancelar
              </button>
              <button
                onClick={() => handleDelete(confirmDelete)}
                className="flex-1 py-2 text-sm rounded-md bg-[var(--neg)] text-white font-medium"
              >
                Excluir
              </button>
            </div>
          </div>
        </div>
      )}

      <TxDialog
        open={dialogOpen}
        onOpenChange={(o) => { setDialogOpen(o); if (!o) setEditing(null) }}
        initial={editing ?? undefined}
        onSubmit={handleSubmit}
        title={editing ? "Editar transação" : "Nova transação"}
      />
    </div>
  )
}
