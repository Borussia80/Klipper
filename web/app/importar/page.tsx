"use client"

import { useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { PageHeader } from "@/components/ui/page-header"
import { KCard } from "@/components/ui/kcard"
import { EmptyState } from "@/components/ui/empty-state"
import { useCreateTransaction } from "@/lib/queries/useTransactions"
import { fmtBRL, fmtDate } from "@/lib/utils"

interface ParsedTx {
  date: string
  amount: number
  type: "GASTO" | "GANHO"
  category: string
  notes: string
  payment_method: string
}

type ImportState = "idle" | "uploading" | "review" | "saving" | "done" | "error"

export default function ImportarPage() {
  const router = useRouter()
  const fileRef = useRef<HTMLInputElement>(null)
  const create = useCreateTransaction()

  const [state, setState] = useState<ImportState>("idle")
  const [errorMsg, setErrorMsg] = useState("")
  const [transactions, setTransactions] = useState<ParsedTx[]>([])
  const [selected, setSelected] = useState<Set<number>>(new Set())

  const apiBase = process.env.NEXT_PUBLIC_API_URL

  async function handleUpload(file: File) {
    if (!apiBase) {
      setErrorMsg("NEXT_PUBLIC_API_URL não configurado. Defina a URL da API.")
      setState("error")
      return
    }

    setState("uploading")
    setErrorMsg("")

    const form = new FormData()
    form.append("file", file)

    try {
      const res = await fetch(`${apiBase}/import/statement`, {
        method: "POST",
        body: form,
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }))
        throw new Error(err.detail ?? "Erro no servidor")
      }
      const data = await res.json()
      const txs: ParsedTx[] = (data.transactions ?? []).map((t: Record<string, unknown>) => ({
        date:           (t.date as string) ?? new Date().toISOString().slice(0, 10),
        amount:         typeof t.amount === "number" ? t.amount : parseFloat(String(t.amount)) || 0,
        type:           (t.type as "GASTO" | "GANHO") ?? "GASTO",
        category:       (t.category as string) ?? "Outros",
        notes:          (t.notes as string) ?? (t.description as string) ?? "",
        payment_method: (t.payment_method as string) ?? "PIX",
      }))
      setTransactions(txs)
      setSelected(new Set(txs.map((_, i) => i)))
      setState("review")
    } catch (e) {
      setErrorMsg(e instanceof Error ? e.message : "Erro desconhecido")
      setState("error")
    }
  }

  async function handleSave() {
    setState("saving")
    const toSave = transactions.filter((_, i) => selected.has(i))
    try {
      for (const tx of toSave) {
        await create.mutateAsync({
          date:           tx.date,
          amount:         tx.amount,
          type:           tx.type,
          category:       tx.category,
          notes:          tx.notes,
          payment_method: tx.payment_method as Parameters<typeof create.mutateAsync>[0]["payment_method"],
          status:         "PAGO",
        })
      }
      setState("done")
    } catch (e) {
      setErrorMsg(e instanceof Error ? e.message : "Erro ao salvar")
      setState("error")
    }
  }

  function toggleRow(i: number) {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(i)) next.delete(i); else next.add(i)
      return next
    })
  }

  return (
    <div className="p-4 md:p-6 max-w-3xl mx-auto">
      <PageHeader title="Importar extrato" subtitle="PDF ou imagem do extrato bancário" />

      {state === "idle" || state === "error" ? (
        <KCard>
          <div
            className="border-2 border-dashed border-[var(--rule)] rounded-lg p-10 flex flex-col items-center gap-4 cursor-pointer hover:border-[var(--brass)] transition-colors"
            onClick={() => fileRef.current?.click()}
            onDrop={(e) => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f) handleUpload(f) }}
            onDragOver={(e) => e.preventDefault()}
          >
            <span className="text-4xl">📄</span>
            <p className="text-sm text-[var(--ink)] font-medium">Arraste o extrato ou clique para selecionar</p>
            <p className="text-xs text-[var(--ink-4)]">PDF, PNG ou JPG · máx 10 MB</p>
            <input
              ref={fileRef}
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              className="sr-only"
              onChange={(e) => { const f = e.target.files?.[0]; if (f) handleUpload(f) }}
            />
          </div>
          {state === "error" && (
            <p className="mt-3 text-sm text-[var(--neg)] text-center">{errorMsg}</p>
          )}
        </KCard>
      ) : state === "uploading" ? (
        <KCard>
          <EmptyState icon="⏳" title="Processando extrato…" description="Aguarde o OCR extrair as transações." />
        </KCard>
      ) : state === "done" ? (
        <KCard>
          <EmptyState
            icon="✅"
            title="Extrato importado com sucesso"
            description={`${selected.size} transações salvas.`}
            action={
              <button
                onClick={() => router.push("/transacoes")}
                className="text-xs px-4 py-2 rounded-md bg-[var(--brass)] text-[var(--bg)] font-medium"
              >
                Ver transações →
              </button>
            }
          />
        </KCard>
      ) : (
        /* Review state */
        <>
          <div className="flex items-center justify-between mb-4">
            <p className="text-xs text-[var(--ink-3)]">
              {selected.size} de {transactions.length} selecionadas
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setSelected(new Set(transactions.map((_, i) => i)))}
                className="text-xs text-[var(--brass)] hover:opacity-80"
              >
                Todas
              </button>
              <button
                onClick={() => setSelected(new Set())}
                className="text-xs text-[var(--ink-3)] hover:text-[var(--ink)]"
              >
                Nenhuma
              </button>
            </div>
          </div>

          <KCard padding="none" className="mb-4">
            <ul>
              {transactions.map((tx, i) => (
                <li
                  key={i}
                  onClick={() => toggleRow(i)}
                  className="flex items-center gap-3 px-4 py-3 border-b border-[var(--rule)] last:border-0 cursor-pointer hover:bg-[var(--surface)] transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={selected.has(i)}
                    onChange={() => toggleRow(i)}
                    onClick={(e) => e.stopPropagation()}
                    className="w-4 h-4 accent-[var(--brass)] shrink-0"
                  />
                  <span className="text-xs px-2 py-0.5 rounded bg-[var(--layer)] text-[var(--ink-3)] shrink-0 max-w-[80px] truncate">
                    {tx.category}
                  </span>
                  <span className="flex-1 text-sm text-[var(--ink)] truncate">
                    {tx.notes || "—"}
                  </span>
                  <span className="text-xs text-[var(--ink-4)] shrink-0">{fmtDate(tx.date)}</span>
                  <span className={`text-sm font-medium tabular shrink-0 ${tx.type === "GANHO" ? "text-[var(--pos)]" : "text-[var(--ink)]"}`}>
                    {tx.type === "GANHO" ? "+" : "−"}{fmtBRL(tx.amount)}
                  </span>
                </li>
              ))}
            </ul>
          </KCard>

          <div className="flex gap-2">
            <button
              onClick={() => setState("idle")}
              className="flex-1 py-2 text-sm rounded-md border border-[var(--rule)] text-[var(--ink-3)]"
            >
              Cancelar
            </button>
            <button
              onClick={handleSave}
              disabled={selected.size === 0 || state === "saving"}
              className="flex-1 py-2 text-sm rounded-md bg-[var(--brass)] text-[var(--bg)] font-medium disabled:opacity-50"
            >
              {state === "saving" ? "Salvando…" : `Importar ${selected.size} transações`}
            </button>
          </div>
        </>
      )}
    </div>
  )
}
