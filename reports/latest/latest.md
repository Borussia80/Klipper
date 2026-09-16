# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `93c0d2cbf24f9beb8d4e1543cc40ae5b10c63684` · **Modo:** fast

## Score geral: 73/100
> Baseline: nenhum run anterior — primeira execução

## Seções

| Seção | Score | Risco | Tendência |
|---|---|---|---|
| Arquitetura | 79 | medium | — |
| Domínio financeiro | 55 | critical | — |
| Segurança | 85 | low | — |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-001 | 🟢 low | architecture | 30 | O padrão isLoading/error/try-catch-finally ao redor de apiFetch está duplicado 16 vezes em 8 composables, sem uma abstração compartilhada, apesar de useApi.ts (apps/klipper-web/composables/useApi.ts) já centralizar bem a camada de fetch/retry/renovação de token. |
| ARCH-002 | 🟡 medium | architecture | 24 | ReportsController mistura dois padrões de arquitetura na mesma classe: metade das actions delega para service objects e a outra metade constrói query e agregação de dados financeiros diretamente no controller. |
| ARCH-003 | 🟡 medium | architecture | 24 | 8 das 14 páginas (excluindo o redirecionamento trivial de index.vue, 7 linhas) não têm nenhum teste, incluindo as duas maiores do diretório — dashboard.vue e importar.vue — mesmo que os cálculos que elas consomem já estejam testados nos composables correspondentes (ex: useDashboardKpis.test.ts). |
| FIN-001 | 🔴 critical | finance | 24 | O custo de investimentos usado no patrimônio líquido (`NetWorthSnapshotService`, consumido pelo snapshot mensal/histórico, e `Api::V1::ReportsController#net_worth`) ignora o sinal de `operation_type`, enquanto `PortfolioService` (usado na tela de investimentos) faz a mesma agregação subtraindo vendas — qualquer usuário com ao menos uma operação de venda registrada vê `total_cost` correto em /investimentos mas `net_worth`/`net_worth_history` inflado pelo valor da venda, e o snapshot mensal persiste esse valor errado permanentemente até ser corrigido e recalculado. `frequency` estimado no piso da escala por falta de dado real de quantos usuários registram operações sell (sem telemetria de uso disponível neste checkout). |
| SEC-001 | 🟡 medium | security | 18 | O endpoint GET /api/v1/quotes repassa o parâmetro `tickers` sem validar formato para a URL de uma API externa (brapi.dev) e não tem throttle próprio, permitindo que um usuário autenticado use a API do Klipper como proxy para enviar strings arbitrárias (dentro do path) em volume irrestrito ao serviço terceiro. |
| SEC-002 | 🟢 low | security | 4 | Dependências de build/dev (esbuild via @nuxt/fonts, vitest, svgo, js-yaml, fast-uri) estão desatualizadas com CVEs conhecidos; nenhuma é exercida no bundle de produção servido ao navegador, mas aumentam a superfície de risco de supply chain no ambiente de dev/CI. |
| SEC-003 | 🟢 low | security | 2.4 | O token de redefinição de senha vai no path da URL em vez do corpo da requisição, ficando exposto em texto puro em qualquer log de acesso (Rails, proxy, CDN) durante a janela de validade. |
