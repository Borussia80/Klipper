"use client"

import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from "recharts"
import { fmtBRL } from "@/lib/utils"

export interface NetWorthPoint {
  month: string   // "Jun/25"
  total: number   // patrimônio total
  caixa: number   // só caixa (para tooltip breakdown)
}

function CustomTooltip({
  active, payload, label,
}: {
  active?: boolean
  payload?: { value: number; name: string }[]
  label?: string
}) {
  if (!active || !payload?.length) return null
  const total       = payload.find(p => p.name === "Patrimônio")?.value ?? 0
  const caixa       = payload.find(p => p.name === "Caixa")?.value ?? 0
  const investido   = total - caixa
  return (
    <div className="bg-[var(--card)] border border-[var(--rule)] rounded-md px-3 py-2 shadow-lg text-xs space-y-0.5">
      <p className="font-semibold text-[var(--ink)] mb-1">{label}</p>
      <p className="text-[var(--brass)]">Total: {fmtBRL(total)}</p>
      <p className="text-[var(--ink-3)]">Caixa: {fmtBRL(caixa)}</p>
      <p className="text-[var(--ink-3)]">Invest.: {fmtBRL(investido)}</p>
    </div>
  )
}

interface NetWorthChartProps {
  points:    NetWorthPoint[]
  className?: string
}

export function NetWorthChart({ points, className }: NetWorthChartProps) {
  if (points.length < 2) return null

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={points} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id="nwGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="var(--brass)" stopOpacity={0.3} />
              <stop offset="95%" stopColor="var(--brass)" stopOpacity={0}   />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="var(--rule)"
            vertical={false}
          />
          <XAxis
            dataKey="month"
            tick={{ fontSize: 10, fill: "var(--ink-4)" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis hide />
          <Tooltip
            content={<CustomTooltip />}
            cursor={{ stroke: "var(--rule)", strokeWidth: 1 }}
          />
          {/* Hidden series for tooltip breakdown */}
          <Area
            type="monotone"
            dataKey="caixa"
            name="Caixa"
            stroke="none"
            fill="none"
            dot={false}
          />
          <Area
            type="monotone"
            dataKey="total"
            name="Patrimônio"
            stroke="var(--brass)"
            strokeWidth={2}
            fill="url(#nwGrad)"
            dot={false}
            activeDot={{ r: 4, fill: "var(--brass)", strokeWidth: 0 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
