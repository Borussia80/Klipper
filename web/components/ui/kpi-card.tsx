"use client"

import { cn, fmtBRL, fmtPct } from "@/lib/utils"
import { KCard } from "./kcard"
import { LineChart, Line, ResponsiveContainer } from "recharts"

type Format = "brl" | "pct" | "number" | "text"

interface KpiCardProps {
  label:       string
  value:       number | string
  format?:     Format
  delta?:      number
  deltaLabel?: string
  accent?:     boolean
  sparkline?:  number[]
  className?:  string
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

export function KpiCard({ label, value, format = "brl", delta, deltaLabel, accent, sparkline, className }: KpiCardProps) {
  const hasDelta     = delta !== undefined
  const hasSparkline = sparkline !== undefined && sparkline.length > 1
  const lastVal      = hasSparkline ? sparkline[sparkline.length - 1] : 0
  const sparkColor   = lastVal >= 0 ? "var(--pos)" : "var(--neg)"
  const sparkData    = hasSparkline ? sparkline.map((v, i) => ({ i, v })) : []

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
      {hasSparkline && (
        <div className="mt-auto pt-3 -mx-0 h-9 w-full">
          <ResponsiveContainer width="100%" height={36}>
            <LineChart data={sparkData} margin={{ top: 2, right: 2, bottom: 2, left: 2 }}>
              <Line
                type="monotone"
                dataKey="v"
                stroke={sparkColor}
                strokeWidth={1.5}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </KCard>
  )
}
