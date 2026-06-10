"use client"

import * as Dialog from "@radix-ui/react-dialog"
import { useForm, type Resolver } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { cn } from "@/lib/utils"
import {
  txSchema,
  TxFormValues,
  CATEGORIES_GASTO,
  CATEGORIES_GANHO,
  PAYMENT_METHODS,
} from "@/lib/tx-schema"
import type { Database } from "@/types/database"

type Transaction = Database["public"]["Tables"]["transactions"]["Row"]

interface TxDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  initial?: Partial<Transaction>
  onSubmit: (values: TxFormValues) => Promise<void>
  title?: string
}

function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-[var(--ink-3)] uppercase tracking-wide">{label}</label>
      {children}
      {error && <span className="text-xs text-[var(--neg)]">{error}</span>}
    </div>
  )
}

const inputCls = "w-full px-3 py-2 text-sm rounded-md bg-[var(--surface)] border border-[var(--rule)] text-[var(--ink)] focus:outline-none focus:ring-1 focus:ring-[var(--brass)]"

export function TxDialog({ open, onOpenChange, initial, onSubmit, title = "Lançamento" }: TxDialogProps) {
  const today = new Date().toISOString().slice(0, 10)

  const {
    register,
    handleSubmit,
    watch,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<TxFormValues>({
    resolver: zodResolver(txSchema) as Resolver<TxFormValues>,
    defaultValues: {
      date:           initial?.date ?? today,
      amount:         initial?.amount ?? (0 as unknown as number),
      type:           (initial?.type as "GASTO" | "GANHO") ?? "GASTO",
      category:       initial?.category ?? "",
      notes:          initial?.notes ?? "",
      payment_method: (initial?.payment_method as TxFormValues["payment_method"]) ?? "PIX",
      status:         (initial?.status as TxFormValues["status"]) ?? "PAGO",
    },
  })

  const txType = watch("type")
  const categories = txType === "GANHO" ? CATEGORIES_GANHO : CATEGORIES_GASTO

  async function onValid(values: TxFormValues) {
    await onSubmit(values)
    reset()
    onOpenChange(false)
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/60 z-40" />
        <Dialog.Content
          className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-xl bg-[var(--card)] border border-[var(--rule)] p-6 shadow-xl focus:outline-none"
          aria-describedby={undefined}
        >
          <Dialog.Title className="text-base font-semibold text-[var(--ink)] mb-4">
            {title}
          </Dialog.Title>

          <form onSubmit={handleSubmit(onValid)} className="flex flex-col gap-4">
            {/* Tipo */}
            <Field label="Tipo" error={errors.type?.message}>
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

            {/* Data + Valor */}
            <div className="grid grid-cols-2 gap-3">
              <Field label="Data" error={errors.date?.message}>
                <input type="date" {...register("date")} className={inputCls} />
              </Field>
              <Field label="Valor (R$)" error={errors.amount?.message}>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  placeholder="0,00"
                  {...register("amount")}
                  className={inputCls}
                />
              </Field>
            </div>

            {/* Categoria */}
            <Field label="Categoria" error={errors.category?.message}>
              <select {...register("category")} className={inputCls}>
                <option value="">Selecionar…</option>
                {categories.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </Field>

            {/* Descrição */}
            <Field label="Descrição" error={errors.notes?.message}>
              <input
                type="text"
                placeholder="Mercado, salário, aluguel…"
                {...register("notes")}
                className={inputCls}
              />
            </Field>

            {/* Método + Status */}
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

            {/* Actions */}
            <div className="flex gap-2 pt-2">
              <Dialog.Close asChild>
                <button
                  type="button"
                  className="flex-1 py-2 text-sm rounded-md border border-[var(--rule)] text-[var(--ink-3)] hover:text-[var(--ink)] transition-colors"
                >
                  Cancelar
                </button>
              </Dialog.Close>
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 py-2 text-sm rounded-md bg-[var(--brass)] text-[var(--bg)] font-medium hover:opacity-90 disabled:opacity-50 transition-opacity"
              >
                {isSubmitting ? "Salvando…" : "Salvar"}
              </button>
            </div>
          </form>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
