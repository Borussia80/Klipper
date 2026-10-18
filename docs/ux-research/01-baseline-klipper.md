# 01 — Linha de base do Klipper

**Aferido em:** 2026-10-17, no commit `dc4c5de` (main), lendo o código.
**Escopo:** o que existe hoje, para a matriz (03) saber o que é novo, o que é ajuste e o que já está pronto.

> **Correção ao enunciado da tarefa:** o `klipper-web` é **Nuxt 3** (`"nuxt": "^3.15.4"` no
> `package.json`), não Nuxt 4. Nada nesta pesquisa depende da versão, mas o plano (06) assume Nuxt 3.

---

## 1. Stack de apresentação

| Item | Hoje |
|---|---|
| Framework | Nuxt 3, SPA, PWA via `@vite-pwa/nuxt` (`orientation: portrait`, `display: standalone`) |
| CSS | CSS puro: `assets/css/tokens.css` (66 linhas) + `assets/css/main.css` (293 linhas). Sem Tailwind, sem biblioteca de componentes |
| Ícones | **Phosphor Icons** (`@phosphor-icons/vue`, licença MIT), centralizados em `components/ui/AppIcon.vue`. O `MobileNav.vue` ainda usa SVG inline via `v-html` |
| Fontes | **Inter** (corpo) e **Space Grotesk** (números, títulos), via `@nuxt/fonts` → Google Fonts. Ambas OFL-1.1 |
| Gráficos | Componentes próprios (`charts/FluxoMensal.vue`, `charts/PatrimonioTimeline.vue`), sem biblioteca de gráfico |
| Testes | Vitest + `@nuxt/test-utils` (testes de componente e de página) |

## 2. Direção visual vigente

**Náutica premium** (`docs/design/ROADMAP_REDESIGN_KLIPPER.md`): azul-marinho profundo + latão, todo dado dentro de
card com borda visível, com `docs/design/klipper_mockup.html` como spec canônica. Mantida sem alteração por decisão
de 2026-10-17 — esta pesquisa não muda paleta.

O `tokens.css` carrega uma **regra de racionalização de cor**: cor só no instrumento primário, em condição anormal,
em elemento interativo e na marca; o resto é escala neutra. As specs de `05-specs/` seguem essa regra
(detalhe em `04-design-tokens.md`).

## 3. Design tokens existentes (`assets/css/tokens.css`)

| Grupo | Tokens | Observação |
|---|---|---|
| Superfícies | `--bg #0A0F1A`, `--bg-frame`, `--sf`, `--sf-hi`, `--ly2` | Todas azuladas (matiz ~215°) |
| Bordas | `--bd`, `--bd-hi` | |
| Texto | `--t1`…`--t4` | `--t4` documentado como "não usar como texto" (2–2,7:1) |
| Interativo | `--sea #3BB8C4` (+ `--blt`, `--bdm`) | Aliases legados `--blue`, `--ly`, `--bd2` |
| Estados | `--ok`, `--warn`, `--alert` (+ washes `--okd`, `--wnd`, `--ald`) | |
| Marca | `--brass`, `--brass-dim` | Também cor categórica "Variáveis" nos gráficos de composição |
| Forma | `--r 14px`, `--r-sm 9px`, `--nav 232px` | **Não há escala de espaçamento nem de tipografia** — valores soltos em cada componente |
| Outros | `--bank-*`, `--crypto`, `--chart-*` | |

**Dívidas visíveis:** muito `style=""` inline nas páginas (ex.: cabeçalho fixo de `transacoes.vue`, banner de erro
do `dashboard.vue`) — já registrado como UX-R1 no `ROADMAP_KLIPPER_WEALTH_OS.md`. `main.css` ainda tem cores
literais herdadas do tema anterior (`rgba(91,155,213,…)` nos hovers de `.btn-g` e `.sel-chip`). `configuracoes.vue`
usa tokens inexistentes (bug conhecido no roadmap).

## 4. Telas (rotas em `pages/`)

| Rota | Rótulo na navegação | O que faz hoje |
|---|---|---|
| `/dashboard` | Painel | Resultado do mês (`InstrumentReadout`), barra do mês decorrido, alarme de dívida, série entradas × saídas, 3 KPIs (maior entrada, fixos, cartões), split Fixo × Cartão × Variável, prioridade de quitação, cobertura de reembolso, banner de saúde dos dados, primeiros passos, filtro por portador |
| `/transacoes` | Movimento | Lista agrupada por dia, filtro Todos/Entradas/Saídas, densidade compacta/confortável, seleção em massa com exclusão, abre modal de edição |
| `/orcamento` | Orçamento | Envelopes por categoria (`BudgetCategoryCard`), resumo alocado/gasto/livre |
| `/contas` | Carteiras | Contas e cartões; dados de fatura, juros do rotativo |
| `/investimentos` | Investimentos | Carteira, aportes, cotação; header com custo real via `PortfolioValueChip` |
| `/relatorios` | Relatórios | Patrimônio no tempo (`PatrimonioTimeline`), mensal |
| `/importar` | Importar | CSV e PDF (adapters Itaú, Nubank, BTG) com prévia e confirmação, deduplicação |
| `/portadores` | Portadores | Membros da família (quem gastou) |
| `/configuracoes` | Configurações | Perfil, senha, exportação, exclusão de conta |
| `/onboarding`, `/login`, `/esqueci-senha`, `/redefinir-senha` | — | Fluxos de entrada |

**Navegação:** desktop = `AppSidebar` (232 px) com menu "Criar" (novo lançamento, conta, cartão, investimento) e
`CommandPalette`; mobile = `MobileNav` inferior com 4 fixos (Painel, Movimento, Orçamento, Investimentos) + folha
"Mais". **Não existe botão flutuante de lançamento no mobile** — o lançamento rápido mora no menu "Criar" do
desktop ou na palette.

**Layout:** `main.css` limita `.shell-main > *` a **760 px** de largura ("linha de leitura única"); o painel
sobrescreve para 1160 px inline. Em 1440 px sobra muito espaço lateral.

## 5. Componentes (`components/`)

- **Layout:** `AppSidebar`, `AppTopbar`, `MobileNav`, `OfflineScreen`, `ServerWakingNotice`
- **Leitura de dado:** `InstrumentReadout`, `KpiCard`, `BarraMesDecorrido`, `DebtRankingCard`, `BudgetCategoryCard`,
  `ReimbursementCoverageCard`, `PortfolioValueChip`, `MemberCard`, `TransactionRow`, `BankIcon`
- **Alarme/estado:** `DebtAlarmBanner`, `DataHealthBanner`, `EmptyState`, `FirstSteps`, `ToastStack`,
  `SkeletonCard`, `SkeletonLine`, `SkeletonTransactionList`
- **Modais:** `BaseModal` (focus trap, ARIA), `ModalMount`, `ModalNovoLancamento`, `ModalEditarLancamento`,
  `ModalNovaConta`, `ModalEditarCartao`, `ModalNovaCategoria`, `ModalNovoAporte`, `ModalNovoMembro`,
  `ModalEditarReembolso`, `ModalConfirmDelete`
- **Outros:** `CommandPalette`, `SectionHeader`, `AppIcon`

## 6. API (`klipper-api/config/routes.rb`, `db/schema.rb`)

| Recurso | Endpoints | Campos relevantes para UX |
|---|---|---|
| Contas | CRUD `/accounts` | `account_type`, `balance`, `institution`, `saldo_fatura_atual`, `pagamento_minimo`, `juros_rotativo_am/aa`, `iof_projetado`, `saldo_atualizado_em`, `active` |
| Categorias | CRUD `/categories` | `category_type`, `natureza` (fixo/cartao_parcelamento/variavel), `color`, `icon`, `reimbursed_by_category_id`. **Sem `parent_id`: um nível só** |
| Transações | CRUD `/transactions`, `POST assign_account` | `amount`, `transaction_type` (debit/credit), `occurred_on`, `category_id`, `account_id`, `member_id`, `installment_number/total`, `parent_transaction_id`, `notes`, `dedupe_hash`. Paginação por cursor em headers `X-Next-Cursor` |
| Orçamentos | CRUD `/budgets`, `GET summary` | `amount_limit` por categoria por mês |
| Investimentos | CRUD `/investments`, `GET portfolio`; `/quotes` | |
| Membros | CRUD `/members` | portador |
| Importação | `POST /imports`, `preview`, `confirm` | |
| Relatórios | `monthly`, `monthly_series`, `data_health`, `net_worth`, `net_worth_history`, `natureza_split`, `reimbursement_coverage`, `debt_ranking` | `net_worth_snapshots` mensais |
| Usuário | `me`, `me/export`, senha, logout, exclusão | |

## 7. Lacunas que importam para esta pesquisa

| Lacuna | Hoje |
|---|---|
| Categorias em dois níveis | Não existe (sem `parent_id`) |
| Transações agendadas / recorrentes | Não existe (só parcelamento via `installment_*`). `CategoryRecurrenceCalculator` *detecta* recorrência, não agenda |
| Transferência entre contas | Não existe como tipo; só debit/credit |
| Lançamento rápido mobile (FAB + teclado numérico) | Não existe; modal genérico |
| Saldo histórico por conta (gráfico por conta) | Não existe; só patrimônio total mensal (`net_worth_snapshots`) |
| Regras de importação (substituir/categorizar) | Parcial: `AutoCategorizerService` (fuzzy + regras, decisão registrada na memória do projeto) |
| Kakebo | Especificado em `docs/KAKEBO.md`, não implementado |
| Escala de espaçamento/tipografia | Não existe |
