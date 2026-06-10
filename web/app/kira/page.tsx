"use client"

import { useState, useRef, useEffect } from "react"
import { PageHeader } from "@/components/ui/page-header"
import { KCard } from "@/components/ui/kcard"
import { EmptyState } from "@/components/ui/empty-state"

interface Message {
  role: "user" | "assistant"
  content: string
}

export default function KiraPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [streaming, setStreaming] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  const apiBase = process.env.NEXT_PUBLIC_API_URL

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  async function send() {
    const msg = input.trim()
    if (!msg || streaming) return
    setInput("")
    setMessages(prev => [...prev, { role: "user", content: msg }])

    if (!apiBase) {
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "API URL não configurada. Defina NEXT_PUBLIC_API_URL no ambiente.",
      }])
      return
    }

    setStreaming(true)
    let accumulated = ""
    setMessages(prev => [...prev, { role: "assistant", content: "…" }])

    try {
      const res = await fetch(`${apiBase}/kira/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg }),
      })
      if (!res.body) throw new Error("No response body")
      const reader = res.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value)
        for (const line of chunk.split("\n")) {
          if (line.startsWith("data: ")) {
            const payload = line.slice(6)
            if (payload === "[DONE]") break
            if (!payload.startsWith("[ERROR]")) {
              accumulated += payload
              setMessages(prev => [
                ...prev.slice(0, -1),
                { role: "assistant", content: accumulated },
              ])
            }
          }
        }
      }
    } catch (e) {
      setMessages(prev => [...prev.slice(0, -1), {
        role: "assistant",
        content: `Erro: ${e instanceof Error ? e.message : "desconhecido"}`,
      }])
    } finally {
      setStreaming(false)
    }
  }

  return (
    <div className="flex flex-col h-full p-4 md:p-6 max-w-3xl mx-auto">
      <PageHeader title="Kira" subtitle="Assistente financeiro IA" />

      <KCard padding="none" className="flex-1 overflow-y-auto mb-4 min-h-0">
        {messages.length === 0 ? (
          <EmptyState
            icon="🤖"
            title="Olá, sou a Kira"
            description="Pergunte sobre seus investimentos, orçamento ou qualquer dúvida financeira."
          />
        ) : (
          <ul className="p-4 flex flex-col gap-4">
            {messages.map((m, i) => (
              <li key={i} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
                <div
                  className={
                    m.role === "user"
                      ? "max-w-[80%] px-4 py-2.5 rounded-2xl rounded-tr-sm bg-[var(--brass)] text-[var(--bg)] text-sm"
                      : "max-w-[80%] px-4 py-2.5 rounded-2xl rounded-tl-sm bg-[var(--layer)] text-[var(--ink)] text-sm"
                  }
                >
                  {m.content}
                </div>
              </li>
            ))}
            <div ref={bottomRef} />
          </ul>
        )}
      </KCard>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && send()}
          placeholder="Pergunte algo…"
          className="flex-1 px-4 py-2.5 text-sm rounded-full bg-[var(--surface)] border border-[var(--rule)] text-[var(--ink)] placeholder:text-[var(--ink-4)] focus:outline-none focus:ring-1 focus:ring-[var(--brass)]"
          disabled={streaming}
        />
        <button
          onClick={send}
          disabled={!input.trim() || streaming}
          className="px-4 py-2.5 rounded-full bg-[var(--brass)] text-[var(--bg)] text-sm font-medium hover:opacity-90 disabled:opacity-40 transition-opacity"
        >
          {streaming ? "…" : "→"}
        </button>
      </div>
    </div>
  )
}
