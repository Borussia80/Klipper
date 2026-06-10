import { cn, fmtBRL, fmtPct } from "@/lib/utils"
import { KCard } from "./kcard"

type Format = "brl" | "pct" | "number" | "text"

interface KpiCardProps {
  label: string
  value: number | string
  format?: Format
  delta?: number
  deltaLabel?: string
  accent?: boolean
  className?: string
}

function formatValue(value: number | string, format: Format): string {
  if (typeof value === "string") return value
  switch (format) {
    case "brl":    return fmtBRL(value)
    case "pct":    return fmtPct(value)
    case "number": return value.toLocaleString("pt-BR")
    default:       return String(value)
  }
}

export function KpiCard({ label, value, format = "brl", delta, deltaLabel, accent, className }: KpiCardProps) {
  const hasDelta = delta !== undefined

  return (
    <KCard className={cn("flex flex-col gap-1 min-h-[88px]", className)}>
      <span className="text-xs font-medium text-[var(--ink-3)] uppercase tracking-wide">{label}</span>
      <span
        className={cn(
          "text-2xl font-semibold tabular leading-tight",
          accent ? "text-[var(--brass)]" : "text-[var(--ink)]"
        )}
      >
        {formatValue(value, format)}
      </span>
      {hasDelta && (
        <span
          className={cn(
            "text-xs tabular",
            delta > 0 ? "text-[var(--pos)]" : delta < 0 ? "text-[var(--ink-3)]" : "text-[var(--ink-4)]"
          )}
        >
          {fmtPct(delta)} {deltaLabel ?? "vs mês anterior"}
        </span>
      )}
    </KCard>
  )
}
