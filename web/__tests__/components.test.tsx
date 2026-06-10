import { describe, it, expect } from "vitest"
import { render, screen } from "@testing-library/react"
import { KCard } from "@/components/ui/kcard"
import { KpiCard } from "@/components/ui/kpi-card"
import { EmptyState } from "@/components/ui/empty-state"
import { PageHeader } from "@/components/ui/page-header"
import { TxRow } from "@/components/ui/tx-row"

// ── KCard ─────────────────────────────────────────────────────────────────────

describe("KCard", () => {
  it("renders children", () => {
    render(<KCard>hello</KCard>)
    expect(screen.getByText("hello")).toBeInTheDocument()
  })

  it("applies surface variant class", () => {
    const { container } = render(<KCard variant="surface">x</KCard>)
    expect(container.firstChild).toHaveClass("bg-[var(--surface)]")
  })

  it("applies custom className", () => {
    const { container } = render(<KCard className="custom-cls">x</KCard>)
    expect(container.firstChild).toHaveClass("custom-cls")
  })
})

// ── KpiCard ───────────────────────────────────────────────────────────────────

describe("KpiCard", () => {
  it("renders label and formatted BRL value", () => {
    render(<KpiCard label="Saldo" value={1500} format="brl" />)
    expect(screen.getByText("Saldo")).toBeInTheDocument()
    expect(screen.getByText(/R\$\s*1\.500,00/)).toBeInTheDocument()
  })

  it("renders percentage value", () => {
    render(<KpiCard label="Poupança" value={23.5} format="pct" />)
    expect(screen.getByText("+23.5%")).toBeInTheDocument()
  })

  it("renders delta when provided", () => {
    render(<KpiCard label="X" value={100} delta={5.2} />)
    expect(screen.getByText(/\+5\.2%/)).toBeInTheDocument()
  })

  it("renders brass accent class when accent=true", () => {
    render(<KpiCard label="X" value={100} accent />)
    const value = screen.getByText(/R\$/)
    expect(value).toHaveClass("text-[var(--brass)]")
  })
})

// ── EmptyState ────────────────────────────────────────────────────────────────

describe("EmptyState", () => {
  it("renders title and description", () => {
    render(<EmptyState title="Vazio" description="Nenhum dado ainda." />)
    expect(screen.getByText("Vazio")).toBeInTheDocument()
    expect(screen.getByText("Nenhum dado ainda.")).toBeInTheDocument()
  })

  it("renders action when provided", () => {
    render(<EmptyState title="T" action={<button>Criar</button>} />)
    expect(screen.getByRole("button", { name: "Criar" })).toBeInTheDocument()
  })
})

// ── PageHeader ────────────────────────────────────────────────────────────────

describe("PageHeader", () => {
  it("renders title", () => {
    render(<PageHeader title="Dashboard" />)
    expect(screen.getByRole("heading", { name: "Dashboard" })).toBeInTheDocument()
  })

  it("renders subtitle and action", () => {
    render(<PageHeader title="T" subtitle="Junho 2026" action={<button>+</button>} />)
    expect(screen.getByText("Junho 2026")).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "+" })).toBeInTheDocument()
  })
})

// ── TxRow ─────────────────────────────────────────────────────────────────────

const makeTx = (overrides = {}): Parameters<typeof TxRow>[0]["tx"] => ({
  id: "uuid-1",
  date: "2026-06-10",
  amount: 250,
  type: "GASTO",
  category: "Alimentação",
  notes: "Mercado",
  payment_method: "PIX",
  account_id: null,
  card_id: null,
  installment_id: null,
  status: "PAGO",
  user_id: "user-1",
  created_at: "2026-06-10T12:00:00Z",
  ...overrides,
})

describe("TxRow", () => {
  it("renders category, notes and amount", () => {
    render(<TxRow tx={makeTx()} />)
    expect(screen.getByText("Alimentação")).toBeInTheDocument()
    expect(screen.getByText("Mercado")).toBeInTheDocument()
    expect(screen.getByText(/250/)).toBeInTheDocument()
  })

  it("gastos: amount is neutral (ink), not red", () => {
    render(<TxRow tx={makeTx({ type: "GASTO" })} />)
    const amount = screen.getByText(/−/)
    expect(amount).not.toHaveClass("text-[var(--neg)]")
    expect(amount).toHaveClass("text-[var(--ink)]")
  })

  it("ganhos: amount is green (pos)", () => {
    render(<TxRow tx={makeTx({ type: "GANHO", amount: 3000, notes: "Salário" })} />)
    const amount = screen.getByText(/\+/)
    expect(amount).toHaveClass("text-[var(--pos)]")
  })
})

// ── lib/utils ─────────────────────────────────────────────────────────────────

describe("fmtBRL", () => {
  it("formats correctly", async () => {
    const { fmtBRL } = await import("@/lib/utils")
    expect(fmtBRL(1234.56)).toMatch(/R\$\s*1\.234,56/)
  })
})

describe("fmtPct", () => {
  it("adds + for positive values", async () => {
    const { fmtPct } = await import("@/lib/utils")
    expect(fmtPct(5.3)).toBe("+5.3%")
    expect(fmtPct(-2.1)).toBe("-2.1%")
  })
})
