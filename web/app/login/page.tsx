"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { supabase } from "@/lib/supabase"

type Step = "credentials" | "totp" | "recovery" | "recovery-sent" | "new-password"

export default function LoginPage() {
  const router = useRouter()
  const [step, setStep] = useState<Step>("credentials")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [newPassword2, setNewPassword2] = useState("")
  const [code, setCode] = useState("")
  const [factorId, setFactorId] = useState("")
  const [challengeId, setChallengeId] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  // Detecta redirect do e-mail de recuperação ou erro de link expirado
  useEffect(() => {
    function checkHash() {
      const hash = window.location.hash
      const params = new URLSearchParams(hash.slice(1))

      if (params.get("type") === "recovery" || params.get("type") === "passwordRecovery") {
        setStep("new-password")
        return
      }

      const errCode = params.get("error_code")
      if (errCode === "otp_expired") {
        setStep("recovery")
        setError("O link expirou. Solicite um novo e-mail de recuperação.")
        return
      }
      const errDesc = params.get("error_description")
      if (errDesc) {
        setStep("recovery")
        setError(decodeURIComponent(errDesc.replace(/\+/g, " ")))
      }
    }
    checkHash()
    window.addEventListener("hashchange", checkHash)
    return () => window.removeEventListener("hashchange", checkHash)
  }, [])

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const { error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) throw error

      const { data: factorsData } = await supabase.auth.mfa.listFactors()
      const totp = factorsData?.totp?.find((f) => f.factor_type === "totp" && f.status === "verified")

      if (totp) {
        const { data: challengeData, error: challengeErr } = await supabase.auth.mfa.challenge({ factorId: totp.id })
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
      const { error } = await supabase.auth.mfa.verify({ factorId, challengeId, code })
      if (error) throw error
      router.push("/")
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Código incorreto ou expirado.")
    } finally {
      setLoading(false)
    }
  }

  async function handleRecovery(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/login`,
      })
      if (error) throw error
      setStep("recovery-sent")
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erro ao enviar e-mail.")
    } finally {
      setLoading(false)
    }
  }

  async function handleNewPassword(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    if (newPassword !== newPassword2) {
      setError("As senhas não coincidem.")
      return
    }
    if (newPassword.length < 8) {
      setError("A senha deve ter no mínimo 8 caracteres.")
      return
    }
    setLoading(true)
    try {
      const { error } = await supabase.auth.updateUser({ password: newPassword })
      if (error) throw error
      router.push("/")
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Erro ao redefinir senha.")
    } finally {
      setLoading(false)
    }
  }

  const inputCls = "rounded-md border border-[var(--rule)] bg-[var(--surface)] px-3 py-2 text-sm text-[var(--ink)] placeholder:text-[var(--ink-4)] focus-visible:outline-2 focus-visible:outline-[var(--brass)]"
  const btnPrimary = "w-full py-2 rounded-md bg-[var(--brass)] text-[var(--bg)] text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
  const btnSecondary = "flex-1 py-2 rounded-md border border-[var(--rule)] text-sm text-[var(--ink-3)] hover:text-[var(--ink)] transition-colors"

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--bg)] px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <span className="text-2xl font-semibold text-[var(--brass)] tracking-wide">KLIPPER</span>
          <p className="text-xs text-[var(--ink-4)] mt-1">Private wealth operating system</p>
        </div>

        <div className="bg-[var(--card)] rounded-lg border border-[var(--rule)] p-6 shadow-[var(--shadow-card)]">

          {/* ── Credentials ─────────────────────────────────────────── */}
          {step === "credentials" && (
            <form onSubmit={handleLogin} className="flex flex-col gap-4">
              <h2 className="text-base font-medium text-[var(--ink)]">Acesse o Klipper</h2>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs text-[var(--ink-3)]" htmlFor="email">E-mail</label>
                <input id="email" type="email" autoComplete="email" required value={email}
                  onChange={(e) => setEmail(e.target.value)} className={inputCls} placeholder="seu@email.com" />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs text-[var(--ink-3)]" htmlFor="password">Senha</label>
                <input id="password" type="password" autoComplete="current-password" required value={password}
                  onChange={(e) => setPassword(e.target.value)} className={inputCls} placeholder="••••••••" />
              </div>
              {error && <p className="text-xs text-[var(--neg)]">{error}</p>}
              <button type="submit" disabled={loading} className={`mt-1 ${btnPrimary}`}>
                {loading ? "Entrando…" : "Entrar"}
              </button>
              <button type="button" onClick={() => { setError(""); setStep("recovery") }}
                className="text-sm text-[var(--brass)] hover:opacity-80 transition-opacity text-center">
                Esqueci minha senha
              </button>
            </form>
          )}

          {/* ── TOTP ────────────────────────────────────────────────── */}
          {step === "totp" && (
            <form onSubmit={handleTotp} className="flex flex-col gap-4">
              <h2 className="text-base font-medium text-[var(--ink)]">Verificação em 2 fatores</h2>
              <p className="text-xs text-[var(--ink-3)]">Abra o aplicativo autenticador e insira o código de 6 dígitos.</p>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs text-[var(--ink-3)]" htmlFor="code">Código TOTP</label>
                <input id="code" type="text" inputMode="numeric" pattern="\d{6}" maxLength={6} required
                  value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
                  className={`${inputCls} text-center tracking-widest tabular`} placeholder="000000" autoFocus />
              </div>
              {error && <p className="text-xs text-[var(--neg)]">{error}</p>}
              <div className="flex gap-2">
                <button type="button" onClick={() => { setStep("credentials"); setError(""); setCode("") }} className={btnSecondary}>Voltar</button>
                <button type="submit" disabled={loading || code.length !== 6} className="flex-1 py-2 rounded-md bg-[var(--brass)] text-[var(--bg)] text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50">
                  {loading ? "Verificando…" : "Verificar"}
                </button>
              </div>
            </form>
          )}

          {/* ── Recovery — solicitar e-mail ──────────────────────────── */}
          {step === "recovery" && (
            <form onSubmit={handleRecovery} className="flex flex-col gap-4">
              <h2 className="text-base font-medium text-[var(--ink)]">Recuperar senha</h2>
              <p className="text-xs text-[var(--ink-3)]">
                Informe o e-mail da conta. Você receberá um link para redefinir a senha.
              </p>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs text-[var(--ink-3)]" htmlFor="rec-email">E-mail</label>
                <input id="rec-email" type="email" autoComplete="email" required value={email}
                  onChange={(e) => setEmail(e.target.value)} className={inputCls} placeholder="seu@email.com" autoFocus />
              </div>
              {error && <p className="text-xs text-[var(--neg)]">{error}</p>}
              <div className="flex gap-2">
                <button type="button" onClick={() => { setStep("credentials"); setError("") }} className={btnSecondary}>Voltar</button>
                <button type="submit" disabled={loading} className="flex-1 py-2 rounded-md bg-[var(--brass)] text-[var(--bg)] text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-50">
                  {loading ? "Enviando…" : "Enviar link"}
                </button>
              </div>
            </form>
          )}

          {/* ── Recovery — e-mail enviado ────────────────────────────── */}
          {step === "recovery-sent" && (
            <div className="flex flex-col gap-4 text-center">
              <div className="text-3xl">📬</div>
              <h2 className="text-base font-medium text-[var(--ink)]">Verifique seu e-mail</h2>
              <p className="text-xs text-[var(--ink-3)]">
                Enviamos um link de recuperação para <span className="text-[var(--ink)] font-medium">{email}</span>.
                Clique no link para redefinir a sua senha.
              </p>
              <button type="button" onClick={() => { setStep("credentials"); setError("") }}
                className={`mt-1 ${btnPrimary}`}>
                Voltar ao login
              </button>
            </div>
          )}

          {/* ── New password — após clicar no link do e-mail ─────────── */}
          {step === "new-password" && (
            <form onSubmit={handleNewPassword} className="flex flex-col gap-4">
              <h2 className="text-base font-medium text-[var(--ink)]">Nova senha</h2>
              <p className="text-xs text-[var(--ink-3)]">Escolha uma nova senha para a sua conta.</p>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs text-[var(--ink-3)]" htmlFor="np1">Nova senha</label>
                <input id="np1" type="password" autoComplete="new-password" required value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)} className={inputCls} placeholder="mínimo 8 caracteres" autoFocus />
              </div>
              <div className="flex flex-col gap-1.5">
                <label className="text-xs text-[var(--ink-3)]" htmlFor="np2">Confirmar senha</label>
                <input id="np2" type="password" autoComplete="new-password" required value={newPassword2}
                  onChange={(e) => setNewPassword2(e.target.value)} className={inputCls} placeholder="repita a senha" />
              </div>
              {error && <p className="text-xs text-[var(--neg)]">{error}</p>}
              <button type="submit" disabled={loading || newPassword.length < 8} className={`mt-1 ${btnPrimary}`}>
                {loading ? "Salvando…" : "Salvar nova senha"}
              </button>
            </form>
          )}

        </div>

        <p className="mt-4 text-center text-[10px] text-[var(--ink-4)]">Discipline compounds wealth.</p>
      </div>
    </div>
  )
}
