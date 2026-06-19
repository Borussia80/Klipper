"use client"

import { cn, fmtBRL, fmtDate } from "@/lib/utils"
import { CAT_COLORS, CAT_ICONS } from "@/lib/tx-schema"
import type { Database } from "@/types/database"

type Transaction = Database["public"]["Tables"]["transactions"]["Row"]

interface TxRowProps {
  tx:        Transaction
  onClick?:  () => void
  onDelete?: () => void
  className?: string
}

export function TxRow({ tx, onClick, onDelete, className }: TxRowProps) {
  const isGanho       = tx.type === "GANHO"
  const isPendingSync = tx.status === "PENDENTE_SYNC"
  const icon          = CAT_ICONS[tx.category]  ?? "📂"
  const color         = CAT_COLORS[tx.category] ?? "#94A3B8"

  return (
    <div
      className={cn(
        "flex items-center gap-3 px-4 py-3 hover:bg-[var(--surface)] transition-colors duration-100",
        isPendingSync && "opacity-60",
        className,
      )}
    >
      {/* Category icon circle */}
      <div
        className="shrink-0 w-9 h-9 rounded-full flex items-center justify-center text-base select-none"
        style={{ backgroundColor: color + "22" }}
        aria-hidden="true"
      >
        <span>{icon}</span>
      </div>

      {/* Main click area — opens edit */}
      <button
        type="button"
        onClick={onClick}
        className={cn(
          "flex-1 min-w-0 flex items-center gap-3 text-left",
          "focus-visible:outline-2 focus-visible:outline-[var(--brass)] focus-visible:rounded",
          onClick ? "cursor-pointer" : "cursor-default",
        )}
      >
        {/* Description + category */}
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-[var(--ink)] truncate leading-snug">
            {tx.notes || "—"}
          </p>
          <p className="text-xs text-[var(--ink-4)] truncate leading-snug">{tx.category}</p>
        </div>

        {/* Amount + date */}
        <div className="shrink-0 text-right">
          <span
            className={cn(
              "block text-sm font-semibold tabular leading-snug",
              isGanho ? "text-[var(--pos)]" : "text-[var(--ink)]",
            )}
          >
            {isGanho ? "+" : "−"}{fmtBRL(tx.amount)}
          </span>
          <span className="block text-xs text-[var(--ink-4)] tabular leading-snug">
            {fmtDate(tx.date)}
          </span>
          {isPendingSync && (
            <span className="block text-[10px] text-[var(--ink-4)]" title="Aguardando sincronização">
              ⏳
            </span>
          )}
        </div>
      </button>

      {/* Delete — always visible, subtle */}
      {onDelete && (
        <button
          type="button"
          onClick={onDelete}
          className="shrink-0 w-7 h-7 flex items-center justify-center rounded text-[var(--ink-4)] hover:text-[var(--neg)] hover:bg-red-500/10 transition-colors"
          aria-label="Excluir transação"
        >
          <svg
            width="13" height="13"
            viewBox="0 0 24 24"
            fill="none" stroke="currentColor"
            strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
          >
            <path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
          </svg>
        </button>
      )}
    </div>
  )
}
