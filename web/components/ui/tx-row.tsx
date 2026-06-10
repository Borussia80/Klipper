import { cn, fmtBRL, fmtDate } from "@/lib/utils"
import type { Database } from "@/types/database"

type Transaction = Database["public"]["Tables"]["transactions"]["Row"]

interface TxRowProps {
  tx: Transaction
  onClick?: () => void
}

export function TxRow({ tx, onClick }: TxRowProps) {
  const isGanho = tx.type === "GANHO"

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "w-full flex items-center gap-3 px-4 py-3 text-left",
        "hover:bg-[var(--surface)] transition-colors duration-100",
        "focus-visible:outline-2 focus-visible:outline-[var(--brass)] focus-visible:outline-offset-[-2px]",
        onClick ? "cursor-pointer" : "cursor-default"
      )}
    >
      {/* Categoria pill */}
      <span className="shrink-0 text-[10px] font-medium px-2 py-0.5 rounded bg-[var(--layer)] text-[var(--ink-3)] whitespace-nowrap max-w-[96px] truncate">
        {tx.category}
      </span>

      {/* Descrição */}
      <span className="flex-1 text-sm text-[var(--ink)] truncate">
        {tx.notes || "—"}
      </span>

      {/* Data */}
      <span className="shrink-0 text-xs text-[var(--ink-4)] tabular">{fmtDate(tx.date)}</span>

      {/* Valor — gastos são neutros (ink), entradas são pos */}
      <span
        className={cn(
          "shrink-0 text-sm font-medium tabular",
          isGanho ? "text-[var(--pos)]" : "text-[var(--ink)]"
        )}
      >
        {isGanho ? "+" : "−"}{fmtBRL(tx.amount)}
      </span>
    </button>
  )
}
