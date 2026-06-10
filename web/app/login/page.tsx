"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { supabase } from "@/lib/supabase"

type Step = "credentials" | "totp"

export default function LoginPage() {
  const router = useRouter()
  const [step, setStep] = useState<Step>("credentials")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [code, setCode] = useState("")
  const [factorId, setFactorId] = useState("")
  const [challengeId, setChallengeId] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) throw error

      // Verifica se há TOTP cadastrado
      const { data: factorsData } = await supabase.auth.mfa.listFactors()
      const totp = factorsData?.totp?.find((f) => f.factor_type === "totp" && f.status === "verified")

      if (totp) {
        const { data: challengeData, error: challengeErr } = await supabase.auth.mfa.challenge({
          factorId: totp.id,
        })
        if (challengeErr) throw challengeErr
        setFactorId(totp.id)
        setChallengeId(challengeData.id)
        setStep("totp")
      } else {
        router.push("/")
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "E-mail ou senha incorretos.")
    } finally {
      setLoading(false)
    }
  }

  async function handleTotp(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const { error } = await supabase.auth.mfa.verify({
        factorId,
        challengeId,
        code,
      })
      if (error) throw error
      router.push("/")
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Código incorreto ou expirado.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--bg)] px-4">
      <div className="w-full max-w-sm">
        {/* Brand */}
        <div className="mb-8 text-center">
          <span className="text-2xl font-semibold text-[var(--brass)] tracking-wide">KLIPPER</span>
          <p className="text-xs text-[var(--ink-4)] mt-1">Private wealth operating system</p>
        </div>

        <div className="bg-[var(--card)] rounded-lg border border-[var(--rule)] p-6 shadow-[var(--shadow-card)]">
          {step === "credentials" ? (
            <form onSubmit={handleLogin} className="flex flex-col gap-4">
              <h2 className="text-base font-medium text-[var(--ink)]">Acesse o Klipper</h2>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs text-[var(--ink-3)]" htmlFor="email">E-mail</label>
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="rounded-md border border-[var(--rule)] bg-[var(--surface)] px-3 py-2 text-sm text-[var(--ink)] placeholder:text-[var(--ink-4)] focus-visible:outline-2 focus-visible:outline-[var(--brass)]"
                  placeholder="seu@email.com"
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs text-[var(--ink-3)]" htmlFor="password">Senha</label>
                <input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="rounded-md border border-[var(--rule)] bg-[var(--surface)] px-3 py-2 text-sm text-[var(--ink)] placeholder:text-[var(--ink-4)] focus-visible:outline-2 focus-visible:outline-[var(--brass)]"
                  placeholder="••••••••"
                />
              </div>
              {error && <p className="text-xs text-[var(--neg)]">{error}</p>}
              <button
                type="submit"
                disabled={loading}
                className="mt-1 w-full py-2 rounded-md bg-[var(--brass)] text-[var(--bg)] text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                {loading ? "Entrando…" : "Entrar"}
              </button>
            </form>
          ) : (
            <form onSubmit={handleTotp} className="flex flex-col gap-4">
              <h2 className="text-base font-medium text-[var(--ink)]">Verificação em 2 fatores</h2>
              <p className="text-xs text-[var(--ink-3)]">
                Abra o aplicativo autenticador e insira o código de 6 dígitos.
              </p>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs text-[var(--ink-3)]" htmlFor="code">Código TOTP</label>
                <input
                  id="code"
                  type="text"
                  inputMode="numeric"
                  pattern="\d{6}"
                  maxLength={6}
                  required
                  value={code}
                  onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
                  className="rounded-md border border-[var(--rule)] bg-[var(--surface)] px-3 py-2 text-sm text-[var(--ink)] text-center tracking-widest tabular placeholder:text-[var(--ink-4)] focus-visible:outline-2 focus-visible:outline-[var(--brass)]"
                  placeholder="000000"
                  autoFocus
                />
              </div>
              {error && <p className="text-xs text-[var(--neg)]">{error}</p>}
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => { setStep("credentials"); setError(""); setCode("") }}
                  className="flex-1 py-2 rounded-md border border-[var(--rule)] text-sm text-[var(--ink-3)] hover:text-[var(--ink)] transition-colors"
                >
                  Voltar
                </button>
                <button
                  type="submit"
                  disabled={loading || code.length !== 6}
                  className="flex-1 py-2 rounded-md bg-[var(--brass)] text-[var(--bg)] text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
                >
                  {loading ? "Verificando…" : "Verificar"}
                </button>
              </div>
            </form>
          )}
        </div>

        <p className="mt-4 text-center text-[10px] text-[var(--ink-4)]">
          Discipline compounds wealth.
        </p>
      </div>
    </div>
  )
}
