"use client"

import { PageHeader } from "@/components/ui/page-header"
import { KCard } from "@/components/ui/kcard"
import { SkeletonCard } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/ui/empty-state"
import { useHealthProfessionals } from "@/lib/queries/useHealth"

const SPECIALTY_LABEL: Record<string, string> = {
  FONOAUDIOLOGIA:      "Fonoaudiologia",
  TERAPIA_OCUPACIONAL: "Terapia Ocupacional",
  PSICOLOGIA:          "Psicologia",
  PSIQUIATRIA:         "Psiquiatria",
  NEUROLOGIA:          "Neurologia",
  FISIOTERAPIA:        "Fisioterapia",
  OUTRO:               "Outro",
}

const SPECIALTY_ICON: Record<string, string> = {
  FONOAUDIOLOGIA:      "🗣",
  TERAPIA_OCUPACIONAL: "🧩",
  PSICOLOGIA:          "🧠",
  PSIQUIATRIA:         "💊",
  NEUROLOGIA:          "⚡",
  FISIOTERAPIA:        "🦴",
  OUTRO:               "◎",
}

export default function SaudePage() {
  const { data: professionals, isLoading } = useHealthProfessionals()

  return (
    <div className="p-4 md:p-6 max-w-3xl mx-auto">
      <PageHeader
        title="Saúde"
        subtitle="Profissionais e reembolsos"
      />

      <h2 className="text-xs font-medium text-[var(--ink-3)] uppercase tracking-wide mb-3">
        Profissionais ativos
      </h2>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {Array.from({ length: 3 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : professionals && professionals.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {professionals.map((p) => (
            <KCard key={p.id} variant="surface">
              <div className="flex items-start gap-3">
                <span className="text-2xl" aria-hidden="true">
                  {SPECIALTY_ICON[p.specialty] ?? "◎"}
                </span>
                <div>
                  <p className="text-sm font-medium text-[var(--ink)]">{p.name}</p>
                  <p className="text-xs text-[var(--ink-3)] mt-0.5">
                    {SPECIALTY_LABEL[p.specialty] ?? p.specialty}
                  </p>
                  {p.council_number && (
                    <p className="text-xs text-[var(--ink-4)] mt-0.5">{p.council_number}</p>
                  )}
                </div>
              </div>
            </KCard>
          ))}
        </div>
      ) : (
        <EmptyState
          title="Nenhum profissional cadastrado"
          description="Adicione profissionais pelo app Streamlit (Saúde → Profissionais)."
        />
      )}
    </div>
  )
}
