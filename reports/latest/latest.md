# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `5342ab0ebd02c2357fb9b07b6c98846d8b108a2c` · **Modo:** fast

## Score geral: 29/100 (-33.67 vs baseline)

## Seções

| Seção | Score | Risco | Tendência |
|---|---|---|---|
| Arquitetura | 72 | high | +6 |
| Domínio financeiro | 7 | high | -35 |
| Segurança | 8 | low | -72 |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| FIN-001 | 🟡 medium | finance | 250 | InstrumentReadout hardcoda o rótulo "% da renda" mesmo quando reutilizado em orcamento.vue para exibir participação no orçamento alocado, não na renda — a matemática está correta, a leitura do usuário não. |
| ARCH-002 | 🟠 high | architecture | 112 | A lógica de validação e parsing de valores financeiros de useLancamentoForm — compartilhada pelos modais de novo e editar lançamento — não tem teste unitário dedicado. |
| SEC-002 | 🟢 low | security | 80 | The unauthenticated /api/v1/health endpoint still returns Rails.env in its JSON body, letting any anonymous caller fingerprint whether the target is production/staging/development. |
| FIN-003 | 🔴 critical | finance | 54 | BankImport::AmountParser assume formato BR sempre que há vírgula, corrompendo silenciosamente (sem erro, sem teste) valores en-US vindos de CSV genérico (`amount`/`value`), violando a regra de ouro de que cálculo/parsing financeiro sem teste de borda não entra. |
| ARCH-007 | 🟡 medium | architecture | 40 | StockQuoteService — a única integração HTTP com serviço externo de toda a API (brapi.dev) — não tem spec dedicado, e os três caminhos de erro tratados pelo controller nunca são exercitados por nenhum teste. |
| ARCH-003 | 🟠 high | architecture | 30 | A fórmula de patrimônio líquido (contas + investimentos) continua duplicada entre NetWorthSnapshotService e ReportsController#net_worth em vez de reutilizar o service existente. |
| SEC-003 | 🟡 medium | security | 30 | klipper-web still carries outdated transitive devDependencies (esbuild, fast-uri, js-yaml, svgo) with published low/high advisories that run on every dev/CI invocation of the Vite/Nuxt toolchain, though none ship into the production bundle; quebec-web's set has shrunk to just the low-severity esbuild advisory since its lockfile was refreshed. |
| ARCH-008 | 🟡 medium | architecture | 24 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados byte a byte entre os dois arquivos. |
| ARCH-004 | 🟡 medium | architecture | 16 | Quatro componentes Vue de entrada/edição de dados financeiros (nova conta, novo membro, editar reembolso, e o wrapper ModalMount) continuam sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-005 | 🟡 medium | architecture | 10 | Cinco páginas centrais do Wealth OS (dashboard, contas, investimentos, orçamento, portadores) continuam sem nenhum teste de página. |
| SEC-004 | 🟡 medium | security | 9 | The authenticated GET /api/v1/quotes endpoint passes the user-supplied `tickers` param unescaped into the path/query of an outbound request to a third-party API, letting a caller inject extra query parameters or `/../` path segments into that request and, for a subset of malformed inputs (e.g. a space), crash the action with an unrescued URI::InvalidURIError instead of a handled error response. |
| SEC-005 | 🟢 low | security | 8 | PasswordResetsController#update (redeeming a reset token) has no rate limiting, unlike every other unauthenticated auth-adjacent action; exploitability is limited in practice because the token is a full Rails `generates_token_for` signed value (not a short guessable code), so this is a defense-in-depth/DB-load gap rather than a realistic brute-forceable path — evidence unavailable on the exact token length/entropy since bundler-audit/brakeman and a live Rails console could not be run in this sandboxed environment to inspect it directly. |
| ARCH-006 | 🟡 medium | architecture | 6 | ReportsController mistura dois padrões arquiteturais no mesmo arquivo: metade das actions agrega dados financeiros inline, a outra metade delega a Calculator services. |
