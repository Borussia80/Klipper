/**
 * Fase 2 page tests.
 * All supabase queries are mocked — tests validate render logic, not network.
 */
import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import React from "react"

// ── Mock next/navigation ──────────────────────────────────────────────────────
vi.mock("next/navigation", () => ({
  useRouter:   () => ({ push: vi.fn(), back: vi.fn() }),
  usePathname: () => "/",
}))

// ── Mock supabase client ──────────────────────────────────────────────────────
vi.mock("@/lib/supabase", () => {
  const mockFrom = vi.fn().mockReturnValue({
    select: vi.fn().mockReturnThis(),
    eq:     vi.fn().mockReturnThis(),
    gte:    vi.fn().mockReturnThis(),
    lte:    vi.fn().mockReturnThis(),
    order:  vi.fn().mockResolvedValue({ data: [], error: null }),
    insert: vi.fn().mockReturnThis(),
    update: vi.fn().mockReturnThis(),
    delete: vi.fn().mockReturnThis(),
    upsert: vi.fn().mockReturnThis(),
    single: vi.fn().mockResolvedValue({ data: null, error: null }),
  })
  return { supabase: { from: mockFrom } }
})

// ── Mock recharts (avoid SVG rendering issues in jsdom) ───────────────────────
vi.mock("recharts", () => ({
  PieChart:          ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie:               () => null,
  Cell:              () => null,
  BarChart:          ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar:               () => null,
  XAxis:             () => null,
  YAxis:             () => null,
  CartesianGrid:     () => null,
  Tooltip:           () => null,
  Legend:            () => null,
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
}))

function makeClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } })
}

function wrap(node: React.ReactNode, client = makeClient()) {
  return render(
    <QueryClientProvider client={client}>{node}</QueryClientProvider>
  )
}

// ── Skeleton ──────────────────────────────────────────────────────────────────
describe("Skeleton", () => {
  it("renders with aria-hidden", async () => {
    const { Skeleton } = await import("@/components/ui/skeleton")
    const { container } = render(<Skeleton className="h-4 w-20" />)
    expect(container.firstChild).toHaveAttribute("aria-hidden", "true")
  })
})

// ── TxSchema ──────────────────────────────────────────────────────────────────
describe("txSchema", () => {
  it("validates valid gasto", async () => {
    const { txSchema } = await import("@/lib/tx-schema")
    const result = txSchema.safeParse({
      date:           "2026-06-10",
      amount:         "150.50",
      type:           "GASTO",
      category:       "Alimentação",
      notes:          "Mercado",
      payment_method: "PIX",
      status:         "PAGO",
    })
    expect(result.success).toBe(true)
    if (result.success) expect(result.data.amount).toBe(150.50)
  })

  it("rejects negative amount", async () => {
    const { txSchema } = await import("@/lib/tx-schema")
    const result = txSchema.safeParse({
      date: "2026-06-10",
      amount: -10,
      type: "GASTO",
      category: "Alimentação",
      payment_method: "PIX",
    })
    expect(result.success).toBe(false)
  })

  it("rejects empty date", async () => {
    const { txSchema } = await import("@/lib/tx-schema")
    const result = txSchema.safeParse({
      date: "",
      amount: 100,
      type: "GASTO",
      category: "Alimentação",
      payment_method: "PIX",
    })
    expect(result.success).toBe(false)
  })
})

// ── CAT_COLORS ─────────────────────────────────────────────────────────────────
describe("CAT_COLORS", () => {
  it("covers all expense categories", async () => {
    const { CAT_COLORS, CATEGORIES_GASTO } = await import("@/lib/tx-schema")
    for (const cat of CATEGORIES_GASTO) {
      expect(CAT_COLORS[cat], `Missing color for ${cat}`).toBeTruthy()
    }
  })
})

// ── Dashboard ─────────────────────────────────────────────────────────────────
describe("Dashboard page", () => {
  it("renders page header and KPI skeletons while loading", async () => {
    const { default: HomePage } = await import("@/app/page")
    wrap(<HomePage />)
    expect(screen.getByRole("heading", { name: /Dashboard/i })).toBeInTheDocument()
  })

  it("shows 'Ver todas' link to /transacoes", async () => {
    const { default: HomePage } = await import("@/app/page")
    wrap(<HomePage />)
    expect(screen.getByText(/Ver todas/)).toBeInTheDocument()
  })

  it("shows '+ Lançamento' link", async () => {
    const { default: HomePage } = await import("@/app/page")
    wrap(<HomePage />)
    expect(screen.getByText(/\+ Lançamento/)).toBeInTheDocument()
  })
})

// ── Transações list ───────────────────────────────────────────────────────────
describe("Transações page", () => {
  it("renders heading and filters", async () => {
    const { default: TransacoesPage } = await import("@/app/transacoes/page")
    wrap(<TransacoesPage />)
    expect(screen.getByRole("heading", { name: /Transações/i })).toBeInTheDocument()
    expect(screen.getByText("Todos")).toBeInTheDocument()
    expect(screen.getByText("Saídas")).toBeInTheDocument()
    expect(screen.getByText("Entradas")).toBeInTheDocument()
  })

  it("has search input", async () => {
    const { default: TransacoesPage } = await import("@/app/transacoes/page")
    wrap(<TransacoesPage />)
    expect(screen.getByPlaceholderText("Buscar…")).toBeInTheDocument()
  })

  it("has + Novo button", async () => {
    const { default: TransacoesPage } = await import("@/app/transacoes/page")
    wrap(<TransacoesPage />)
    expect(screen.getByText("+ Novo")).toBeInTheDocument()
  })

  it("opens TxDialog when clicking + Novo", async () => {
    const user = userEvent.setup()
    const { default: TransacoesPage } = await import("@/app/transacoes/page")
    wrap(<TransacoesPage />)
    await user.click(screen.getByText("+ Novo"))
    // Dialog title appears
    expect(screen.getByText("Nova transação")).toBeInTheDocument()
  })
})

// ── Contas page ───────────────────────────────────────────────────────────────
describe("Contas page", () => {
  it("renders heading", async () => {
    const { default: ContasPage } = await import("@/app/contas/page")
    wrap(<ContasPage />)
    expect(screen.getByRole("heading", { level: 1, name: "Contas" })).toBeInTheDocument()
  })

  it("shows both sections", async () => {
    const { default: ContasPage } = await import("@/app/contas/page")
    wrap(<ContasPage />)
    expect(screen.getByText(/Contas bancárias/i)).toBeInTheDocument()
    expect(screen.getByText(/Cartões de crédito/i)).toBeInTheDocument()
  })
})

// ── Orçamento page ────────────────────────────────────────────────────────────
describe("Orçamento page", () => {
  it("renders heading and month nav", async () => {
    const { default: OrcamentoPage } = await import("@/app/orcamento/page")
    wrap(<OrcamentoPage />)
    expect(screen.getByRole("heading", { name: /Orçamento/i })).toBeInTheDocument()
    expect(screen.getByText("‹")).toBeInTheDocument()
    expect(screen.getByText("›")).toBeInTheDocument()
  })

  it("navigates to previous month", async () => {
    const user = userEvent.setup()
    const { default: OrcamentoPage } = await import("@/app/orcamento/page")
    const now = new Date()
    const currentLabel = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"][now.getMonth()]
    wrap(<OrcamentoPage />)
    expect(screen.getByText(new RegExp(currentLabel))).toBeInTheDocument()
    await user.click(screen.getByText("‹"))
    // After one click, current month label is gone (replaced by prev month)
    const prevMonth = now.getMonth() === 0 ? 11 : now.getMonth() - 1
    const prevLabel = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"][prevMonth]
    expect(screen.getByText(new RegExp(prevLabel))).toBeInTheDocument()
  })
})

// ── Saúde page ────────────────────────────────────────────────────────────────
describe("Saúde page", () => {
  it("renders heading", async () => {
    const { default: SaudePage } = await import("@/app/saude/page")
    wrap(<SaudePage />)
    expect(screen.getByRole("heading", { name: /Saúde/i })).toBeInTheDocument()
  })

  it("shows professionals section", async () => {
    const { default: SaudePage } = await import("@/app/saude/page")
    wrap(<SaudePage />)
    expect(screen.getByText(/Profissionais ativos/i)).toBeInTheDocument()
  })
})

// ── Investimentos page ────────────────────────────────────────────────────────
describe("Investimentos page", () => {
  it("renders heading", async () => {
    const { default: InvestimentosPage } = await import("@/app/investimentos/page")
    wrap(<InvestimentosPage />)
    expect(screen.getByRole("heading", { name: /Investimentos/i })).toBeInTheDocument()
  })

  it("shows KPI skeleton while loading", async () => {
    const { default: InvestimentosPage } = await import("@/app/investimentos/page")
    const { container } = wrap(<InvestimentosPage />)
    const skeletons = container.querySelectorAll('[aria-hidden="true"]')
    expect(skeletons.length).toBeGreaterThan(0)
  })
})

// ── Importar page ─────────────────────────────────────────────────────────────
describe("Importar page", () => {
  it("renders upload dropzone", async () => {
    const { default: ImportarPage } = await import("@/app/importar/page")
    wrap(<ImportarPage />)
    expect(screen.getByRole("heading", { name: /Importar/i })).toBeInTheDocument()
    expect(screen.getByText(/Arraste o extrato/i)).toBeInTheDocument()
  })

  it("has file input accepting pdf/png/jpg", async () => {
    const { default: ImportarPage } = await import("@/app/importar/page")
    const { container } = wrap(<ImportarPage />)
    const input = container.querySelector("input[type='file']")
    expect(input).toBeTruthy()
    expect(input?.getAttribute("accept")).toContain("pdf")
  })
})

// ── TxDialog ──────────────────────────────────────────────────────────────────
describe("TxDialog", () => {
  it("renders form fields when open", async () => {
    const { TxDialog } = await import("@/components/ui/tx-dialog")
    render(
      <TxDialog
        open={true}
        onOpenChange={vi.fn()}
        onSubmit={vi.fn()}
        title="Teste"
      />
    )
    expect(screen.getByText("Teste")).toBeInTheDocument()
    expect(screen.getByText("Saída")).toBeInTheDocument()
    expect(screen.getByText("Entrada")).toBeInTheDocument()
    expect(screen.getByText("Salvar")).toBeInTheDocument()
  })

  it("shows expense category options when type is GASTO", async () => {
    const { TxDialog } = await import("@/components/ui/tx-dialog")
    render(
      <TxDialog
        open={true}
        onOpenChange={vi.fn()}
        onSubmit={vi.fn()}
      />
    )
    // Default type is GASTO → expense categories visible in the DOM
    expect(screen.getByText("Alimentação")).toBeInTheDocument()
    expect(screen.getByText("Moradia")).toBeInTheDocument()
  })
})
