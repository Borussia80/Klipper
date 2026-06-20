"use client"

import { useState } from "react"
import { PageHeader } from "@/components/ui/page-header"
import { KCard } from "@/components/ui/kcard"
import { EmptyState } from "@/components/ui/empty-state"
import { SkeletonCard } from "@/components/ui/skeleton"
import {
  useRules, useCreateRule, useDeleteRule, useToggleRule,
  RULE_FIELDS, RULE_OPERATORS,
  type RuleField, type RuleOperator,
} from "@/lib/queries/useRules"
import { CATEGORIES_GASTO, CATEGORIES_GANHO } from "@/lib/tx-schema"
import { cn } from "@/lib/utils"

const OPERATOR_LABELS: Record<RuleOperator, string> = {
  contains:     "contém",
  starts_with:  "começa com",
  equals:       "igual a",
  greater_than: "maior que",
  less_than:    "menor que",
  regex:        "regex",
}

const FIELD_LABELS: Record<RuleField, string> = {
  notes:  "Descrição",
  amount: "Valor (R$)",
}

interface NewRuleState {
  field:    RuleField
  operator: RuleOperator
  value:    string
  category: string
  priority: number
}

const ALL_CATEGORIES = [...CATEGORIES_GASTO, ...CATEGORIES_GANHO]

export default function RegrasPage() {
  const { data: rules, isLoading } = useRules()
  const createRule  = useCreateRule()
  const deleteRule  = useDeleteRule()
  const toggleRule  = useToggleRule()

  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState<NewRuleState>({
    field:    "notes",
    operator: "contains",
    value:    "",
    category: "Alimentação",
    priority: 100,
  })
  const [saving, setSaving] = useState(false)

  async function handleSave() {
    if (!form.value.trim()) return
    setSaving(true)
    try {
      await createRule.mutateAsync({
        field:    form.field,
        operator: form.operator,
        value:    form.value.trim(),
        category: form.category,
        priority: form.priority,
      })
      setForm({ field: "notes", operator: "contains", value: "", category: "Alimentação", priority: 100 })
      setShowForm(false)
    } finally {
      setSaving(false)
    }
  }

  const inputCls = "w-full px-3 py-2 text-sm rounded-md bg-[var(--surface)] border border-[var(--rule)] text-[var(--ink)] focus:outline-none focus:ring-1 focus:ring-[var(--brass)]"
  const labelCls = "text-xs font-medium text-[var(--ink-3)] uppercase tracking-wide"

  return (
    <div className="p-4 md:p-6 max-w-2xl mx-auto">
      <PageHeader
        title="Regras de categorização"
        action={
          <button
            type="button"
            onClick={() => setShowForm(s => !s)}
            className="text-xs px-3 py-1.5 rounded-md bg-[var(--brass)] text-[var(--bg)] font-medium hover:opacity-90"
          >
            {showForm ? "Cancelar" : "+ Nova regra"}
          </button>
        }
      />

      <p className="text-xs text-[var(--ink-4)] mb-4 -mt-2">
        Regras são aplicadas em ordem de prioridade (menor número = primeiro) antes da sugestão por histórico.
      </p>

      {/* New rule form */}
      {showForm && (
        <KCard className="mb-4">
          <p className="text-sm font-medium text-[var(--ink)] mb-3">Nova regra</p>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div className="flex flex-col gap-1">
              <label className={labelCls}>Campo</label>
              <select
                value={form.field}
                onChange={e => setForm(f => ({ ...f, field: e.target.value as RuleField }))}
                className={inputCls}
              >
                {RULE_FIELDS.map(f => (
                  <option key={f} value={f}>{FIELD_LABELS[f]}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1">
              <label className={labelCls}>Operador</label>
              <select
                value={form.operator}
                onChange={e => setForm(f => ({ ...f, operator: e.target.value as RuleOperator }))}
                className={inputCls}
              >
                {RULE_OPERATORS.map(op => (
                  <option key={op} value={op}>{OPERATOR_LABELS[op]}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1">
              <label className={labelCls}>Valor / Padrão</label>
              <input
                type="text"
                value={form.value}
                onChange={e => setForm(f => ({ ...f, value: e.target.value }))}
                placeholder={form.field === "amount" ? "ex: 5000" : "ex: uber"}
                className={inputCls}
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className={labelCls}>Categoria resultante</label>
              <select
                value={form.category}
                onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
                className={inputCls}
              >
                {ALL_CATEGORIES.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1">
              <label className={labelCls}>Prioridade</label>
              <input
                type="number"
                min={1}
                max={999}
                value={form.priority}
                onChange={e => setForm(f => ({ ...f, priority: Number(e.target.value) }))}
                className={inputCls}
              />
            </div>
          </div>
          <button
            type="button"
            onClick={handleSave}
            disabled={saving || !form.value.trim()}
            className="w-full py-2 text-sm rounded-md bg-[var(--brass)] text-[var(--bg)] font-medium hover:opacity-90 disabled:opacity-40"
          >
            {saving ? "Salvando…" : "Salvar regra"}
          </button>
        </KCard>
      )}

      {/* Rules list */}
      {isLoading ? (
        <SkeletonCard />
      ) : !rules?.length ? (
        <EmptyState
          title="Nenhuma regra configurada"
          description="Crie regras para categorizar transações automaticamente ao digitá-las."
        />
      ) : (
        <KCard padding="none">
          <div className="divide-y divide-[var(--rule)]">
            {rules.map(rule => (
              <div
                key={rule.id}
                className={cn(
                  "flex items-center gap-3 px-4 py-3",
                  !rule.is_active && "opacity-50",
                )}
              >
                {/* Priority badge */}
                <span className="shrink-0 w-7 h-7 rounded-full bg-[var(--surface)] flex items-center justify-center text-[10px] font-bold text-[var(--ink-3)]">
                  {rule.priority}
                </span>

                {/* Rule description */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-[var(--ink)] truncate">
                    <span className="font-medium">{FIELD_LABELS[rule.field as RuleField]}</span>
                    {" "}
                    <span className="text-[var(--ink-4)]">{OPERATOR_LABELS[rule.operator as RuleOperator]}</span>
                    {" "}
                    <span className="font-medium text-[var(--brass)]">&quot;{rule.value}&quot;</span>
                  </p>
                  <p className="text-xs text-[var(--ink-4)]">→ {rule.category}</p>
                </div>

                {/* Toggle + delete */}
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    onClick={() => toggleRule.mutate({ id: rule.id, is_active: !rule.is_active })}
                    className={cn(
                      "text-xs px-2 py-1 rounded border transition-colors",
                      rule.is_active
                        ? "border-[var(--pos)] text-[var(--pos)]"
                        : "border-[var(--rule)] text-[var(--ink-4)]",
                    )}
                  >
                    {rule.is_active ? "Ativa" : "Inativa"}
                  </button>
                  <button
                    type="button"
                    onClick={() => deleteRule.mutate(rule.id)}
                    className="w-7 h-7 flex items-center justify-center rounded text-[var(--ink-4)] hover:text-[var(--neg)] hover:bg-red-500/10 transition-colors"
                    aria-label="Excluir regra"
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </KCard>
      )}
    </div>
  )
}
