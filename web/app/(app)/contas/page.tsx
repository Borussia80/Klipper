"use client"

import { PageHeader } from "@/components/ui/page-header"
import { KCard } from "@/components/ui/kcard"
import { SkeletonCard } from "@/components/ui/skeleton"
import { EmptyState } from "@/components/ui/empty-state"
import { useBankAccounts, useCreditCards } from "@/lib/queries/useAccounts"
import { fmtBRL } from "@/lib/utils"

const ACCOUNT_TYPE_LABEL: Record<string, string> = {
  CORRENTE:    "Conta Corrente",
  POUPANCA:    "Poupança",
  INVESTIMENTO: "Investimento",
}

export default function ContasPage() {
  const { data: accounts, isLoading: accLoading } = useBankAccounts()
  const { data: cards, isLoading: cardLoading } = useCreditCards()

  const totalCaixa = accounts?.reduce((s, a) => s + a.balance, 0) ?? 0
  const isLoading = accLoading || cardLoading

  return (
    <div className="p-4 md:p-6 max-w-3xl mx-auto">
      <PageHeader
        title="Contas"
        subtitle={isLoading ? undefined : `Caixa total: ${fmtBRL(totalCaixa)}`}
      />

      {/* Bank accounts */}
      <h2 className="text-xs font-medium text-[var(--ink-3)] uppercase tracking-wide mb-3">
        Contas bancárias
      </h2>
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
          {Array.from({ length: 2 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : accounts && accounts.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
          {accounts.map((acc) => (
            <KCard key={acc.id} variant="surface">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-[var(--ink)]">{acc.name}</p>
                  <p className="text-xs text-[var(--ink-4)] mt-0.5">{acc.bank} · {ACCOUNT_TYPE_LABEL[acc.type] ?? acc.type}</p>
                </div>
                <span
                  className="w-3 h-3 rounded-full mt-1"
                  style={{ background: acc.color || "var(--brass)" }}
                />
              </div>
              <p className="text-xl font-semibold tabular text-[var(--ink)] mt-3">
                {fmtBRL(acc.balance)}
              </p>
            </KCard>
          ))}
        </div>
      ) : (
        <EmptyState
          title="Nenhuma conta cadastrada"
          description="Adicione contas pelo app Streamlit (Fase 4: migração completa)."
          className="mb-6"
        />
      )}

      {/* Credit cards */}
      <h2 className="text-xs font-medium text-[var(--ink-3)] uppercase tracking-wide mb-3">
        Cartões de crédito
      </h2>
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {Array.from({ length: 2 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : cards && cards.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {cards.map((card) => (
            <KCard key={card.id} variant="surface">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-[var(--ink)]">{card.name}</p>
                  <p className="text-xs text-[var(--ink-4)] mt-0.5">{card.bank} · fecha dia {card.closing_day}</p>
                </div>
                <span
                  className="w-3 h-3 rounded-full mt-1"
                  style={{ background: card.color || "#6366F1" }}
                />
              </div>
              <div className="mt-3 flex justify-between text-xs text-[var(--ink-3)]">
                <span>Limite</span>
                <span className="tabular text-[var(--ink)]">{fmtBRL(card.limit_total)}</span>
              </div>
              <div className="flex justify-between text-xs text-[var(--ink-3)] mt-1">
                <span>Vence dia</span>
                <span className="text-[var(--ink)]">{card.due_day}</span>
              </div>
            </KCard>
          ))}
        </div>
      ) : (
        <EmptyState
          title="Nenhum cartão cadastrado"
          description="Adicione cartões pelo app Streamlit."
        />
      )}
    </div>
  )
}
