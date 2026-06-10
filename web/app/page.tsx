import { PageHeader } from "@/components/ui/page-header"
import { KpiCard } from "@/components/ui/kpi-card"
import { EmptyState } from "@/components/ui/empty-state"

export default function HomePage() {
  return (
    <div className="p-4 md:p-6 max-w-5xl mx-auto">
      <PageHeader
        title="Dashboard"
        subtitle="Junho 2026"
      />

      {/* KPI grid — dados reais conectados na Fase 2 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <KpiCard label="Saldo Total" value={0} format="brl" />
        <KpiCard label="Entradas" value={0} format="brl" />
        <KpiCard label="Gastos" value={0} format="brl" />
        <KpiCard label="Taxa de Poupança" value={0} format="pct" />
      </div>

      <EmptyState
        icon="🔒"
        title="Aguardando Fase 0 (RLS)"
        description="Aplique as migrations 005a e 005b no Supabase para conectar os dados reais."
      />
    </div>
  )
}
