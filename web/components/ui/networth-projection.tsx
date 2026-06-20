"use client"

import {
  AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, ReferenceDot,
} from "recharts"
import { KCard } from "./kcard"
import { fmtBRL, chartTooltipStyle } from "@/lib/utils"
import type { ProjectionPoint } from "@/lib/finance/projection"

interface NetWorthProjectionProps {
  points: ProjectionPoint[]
  current: number
  monthlyNet: number
}

export function NetWorthProjection({ points, current, monthlyNet }: NetWorthProjectionProps) {
  const final = points[points.length - 1]?.value ?? current
  const months = points.length - 1
  const delta = final - current
  const positivo = monthlyNet >= 0

  return (
    <KCard className="mb-6">
      <div className="mb-3 flex items-baseline justify-between gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-[var(--ink-3)]">
            Patrimônio projetado · {months} meses
          </p>
          {/* Transparência: a premissa por trás da projeção, em linguagem direta */}
          <p className="mt-1 text-xs text-[var(--ink-4)]">
            {positivo
              ? `Mantendo o aporte médio de ${fmtBRL(monthlyNet)}/mês`
              : `No ritmo atual você consome ${fmtBRL(Math.abs(monthlyNet))}/mês`}
          </p>
        </div>
        <div className="shrink-0 text-right">
          <p className="text-lg font-semibold tabular text-[var(--ink)]">{fmtBRL(final)}</p>
          <p
            className="text-xs tabular"
            style={{ color: delta >= 0 ? "var(--pos)" : "var(--neg)" }}
          >
            {delta >= 0 ? "+" : "−"}{fmtBRL(Math.abs(delta))}
          </p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={points} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="projFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--brass)" stopOpacity={0.25} />
              <stop offset="100%" stopColor="var(--brass)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis
            dataKey="label"
            tick={{ fill: "var(--ink-4)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            interval={1}
          />
          <YAxis
            tick={{ fill: "var(--ink-4)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={44}
            tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
          />
          <Tooltip
            formatter={(v) => (typeof v === "number" ? fmtBRL(v) : v)}
            labelFormatter={(l) => `Mês: ${l}`}
            contentStyle={chartTooltipStyle}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="var(--brass)"
            strokeWidth={2}
            fill="url(#projFill)"
            dot={false}
          />
          {/* Marca o ponto "hoje" para separar real de projeção */}
          <ReferenceDot
            x={points[0]?.label}
            y={current}
            r={4}
            fill="var(--brass)"
            stroke="var(--bg)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </KCard>
  )
}
