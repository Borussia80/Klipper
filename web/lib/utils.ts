import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** Shared contentStyle for all Recharts Tooltip components. */
export const chartTooltipStyle = {
  background:   "var(--card)",
  border:       "1px solid var(--rule)",
  borderRadius: "6px",
  fontSize:     "12px",
  color:        "var(--ink)",
  boxShadow:    "0 4px 12px rgba(0,0,0,0.2)",
  padding:      "8px 10px",
}

export function fmtBRL(value: number): string {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value)
}

export function fmtPct(value: number, decimals = 1): string {
  return `${value >= 0 ? "+" : ""}${value.toFixed(decimals)}%`
}

export function fmtDate(iso: string): string {
  return new Date(iso).toLocaleDateString("pt-BR")
}
