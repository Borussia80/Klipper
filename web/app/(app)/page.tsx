"use client"

import { useState } from "react"
import { PageHeader } from "@/components/ui/page-header"
import { KpiCard } from "@/components/ui/kpi-card"
import { TxRow } from "@/components/ui/tx-row"
import { SkeletonCard, SkeletonRow } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/ui/empty-state"
import { KCard } from "@/components/ui/kcard"
import { useTransactions } from "@/lib/queries/useTransactions"
import { useBankAccounts } from "@/lib/queries/useAccounts"
import { fmtBRL } from "@/lib/utils"
import { CAT_COLORS } from "@/lib/tx-schema"
import Link from "next/link"
import {
  PieChart, Pie, Cell, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer,
} from "recharts"

const MESES_PT = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

function useNow() {
  const now = new Date()
  return { year: now.getFullYear(), month: now.getMonth() + 1 }
}

export default function HomePage() {
  const { year, month } = useNow()
  const [showDialog, setShowDialog] = useState(false)

  const { data: txs, isLoading: txLoading, error: txError } = useTransactions(year, month)
  const { data: accounts, isLoading: accLoading } = useBankAccounts()

  const ganhos = txs?.filter(t => t.type === "GANHO").reduce((s, t) => s + t.amount, 0) ?? 0
  const gastos = txs?.filter(t => t.type === "GASTO").reduce((s, t) => s + t.amount, 0) ?? 0
  const saldo  = ganhos - gastos
  const caixa  = accounts?.reduce((s, a) => s + a.balance, 0) ?? 0
  const poupanca = ganhos > 0 ? ((ganhos - gastos) / ganhos) * 100 : 0

  // Category breakdown for pie chart
  const catMap: Record<string, number> = {}
  txs?.filter(t => t.type === "GASTO").forEach(t => {
    catMap[t.category] = (catMap[t.category] ?? 0) + t.amount
  })
  const pieData = Object.entries(catMap)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)

  const recentTxs = txs?.slice(0, 5) ?? []
  const subtitle = `${MESES_PT[month - 1]} ${year}`
  const isLoading = txLoading || accLoading

  return (
    <div className="p-4 md:p-6 max-w-5xl mx-auto">
      <PageHeader
        title="Dashboard"
        subtitle={subtitle}
        action={
          <Link
            href="/transacoes/novo"
            className="text-xs px-3 py-1.5 rounded-md bg-[var(--brass)] text-[var(--bg)] font-medium hover:opacity-90 transition-opacity"
          >
            + Lançamento
          </Link>
        }
      />

      {/* KPI grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
        ) : txError ? (
          <div className="col-span-4">
            <EmptyState
              icon="⚠"
              title="Erro ao carregar dados"
              description="Verifique se as migrations Fase 0 foram aplicadas e tente novamente."
            />
          </div>
        ) : (
          <>
            <KpiCard label="Caixa disponível" value={caixa} format="brl" />
            <KpiCard label="Entradas · mês" value={ganhos} format="brl" accent />
            <KpiCard label="Saídas · mês" value={gastos} format="brl" />
            <KpiCard label="Taxa de poupança" value={poupanca} format="pct" />
          </>
        )}
      </div>

      {/* Charts */}
      {!isLoading && !txError && txs && txs.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Donut — gastos por categoria */}
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

          {/* Bar — saldo do mês */}
          <KCard>
            <p className="text-xs font-medium text-[var(--ink-3)] uppercase tracking-wide mb-3">
              Entradas × Saídas
            </p>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart
                data={[{ mes: subtitle, Entradas: ganhos, Saídas: gastos }]}
                margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="mes" tick={{ fill: "var(--ink-4)", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: "var(--ink-4)", fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
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
                <Bar dataKey="Entradas" fill="var(--pos)" radius={[3,3,0,0]} />
                <Bar dataKey="Saídas" fill="#3B82F6" radius={[3,3,0,0]} />
              </BarChart>
            </ResponsiveContainer>
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
          <ul>
            {recentTxs.map((tx) => (
              <li key={tx.id} className="border-b border-[var(--rule)] last:border-0">
                <TxRow tx={tx} />
              </li>
            ))}
          </ul>
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
