"use client"

import { useRouter } from "next/navigation"
import { PageHeader } from "@/components/ui/page-header"
import { KCard } from "@/components/ui/kcard"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import type { Resolver } from "react-hook-form"
import { txSchema, TxFormValues, CATEGORIES_GASTO, CATEGORIES_GANHO, PAYMENT_METHODS } from "@/lib/tx-schema"
import { useCreateTransaction } from "@/lib/queries/useTransactions"
import { cn } from "@/lib/utils"

const inputCls = "w-full px-3 py-2 text-sm rounded-md bg-[var(--surface)] border border-[var(--rule)] text-[var(--ink)] focus:outline-none focus:ring-1 focus:ring-[var(--brass)]"

function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-[var(--ink-3)] uppercase tracking-wide">{label}</label>
      {children}
      {error && <span className="text-xs text-[var(--neg)]">{error}</span>}
    </div>
  )
}

export default function NovoTransacaoPage() {
  const router = useRouter()
  const create = useCreateTransaction()
  const today = new Date().toISOString().slice(0, 10)

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<TxFormValues>({
    resolver: zodResolver(txSchema) as Resolver<TxFormValues>,
    defaultValues: {
      date: today,
      type: "GASTO",
      payment_method: "PIX",
      status: "PAGO",
    },
  })

  const txType = watch("type")
  const categories = txType === "GANHO" ? CATEGORIES_GANHO : CATEGORIES_GASTO

  async function onSubmit(values: TxFormValues) {
    await create.mutateAsync(values as Parameters<typeof create.mutateAsync>[0])
    router.push("/transacoes")
  }

  return (
    <div className="p-4 md:p-6 max-w-lg mx-auto">
      <PageHeader title="Nova transação" />
      <KCard>
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
          {/* Tipo */}
          <Field label="Tipo">
            <div className="flex gap-2">
              {(["GASTO", "GANHO"] as const).map((t) => (
                <label
                  key={t}
                  className={cn(
                    "flex-1 py-2 text-center text-sm font-medium rounded-md cursor-pointer border transition-colors",
                    watch("type") === t
                      ? "bg-[var(--brass)] text-[var(--bg)] border-[var(--brass)]"
                      : "bg-[var(--surface)] text-[var(--ink-3)] border-[var(--rule)] hover:border-[var(--ink-4)]"
                  )}
                >
                  <input type="radio" value={t} {...register("type")} className="sr-only" />
                  {t === "GASTO" ? "Saída" : "Entrada"}
                </label>
              ))}
            </div>
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Data" error={errors.date?.message}>
              <input type="date" {...register("date")} className={inputCls} />
            </Field>
            <Field label="Valor (R$)" error={errors.amount?.message}>
              <input type="number" step="0.01" min="0.01" placeholder="0,00" {...register("amount")} className={inputCls} />
            </Field>
          </div>

          <Field label="Categoria" error={errors.category?.message}>
            <select {...register("category")} className={inputCls}>
              <option value="">Selecionar…</option>
              {categories.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </Field>

          <Field label="Descrição" error={errors.notes?.message}>
            <input type="text" placeholder="Mercado, salário, aluguel…" {...register("notes")} className={inputCls} />
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Método" error={errors.payment_method?.message}>
              <select {...register("payment_method")} className={inputCls}>
                {PAYMENT_METHODS.map((m) => (
                  <option key={m.value} value={m.value}>{m.label}</option>
                ))}
              </select>
            </Field>
            <Field label="Status" error={errors.status?.message}>
              <select {...register("status")} className={inputCls}>
                <option value="PAGO">Pago</option>
                <option value="PENDENTE">Pendente</option>
                <option value="AGENDADO">Agendado</option>
              </select>
            </Field>
          </div>

          <div className="flex gap-2 pt-2">
            <button
              type="button"
              onClick={() => router.back()}
              className="flex-1 py-2 text-sm rounded-md border border-[var(--rule)] text-[var(--ink-3)] hover:text-[var(--ink)]"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 py-2 text-sm rounded-md bg-[var(--brass)] text-[var(--bg)] font-medium hover:opacity-90 disabled:opacity-50"
            >
              {isSubmitting ? "Salvando…" : "Salvar"}
            </button>
          </div>
        </form>
      </KCard>
    </div>
  )
}
