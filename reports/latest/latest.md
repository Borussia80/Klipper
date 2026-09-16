# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `593ef37b872f2256d05df525607cb3850c5afe7d` · **Modo:** fast

## Score geral: 62.67/100
> Baseline: nenhum run anterior — primeira execução

## Seções

| Seção | Score | Risco | Tendência |
|---|---|---|---|
| Arquitetura | 66 | high | — |
| Domínio financeiro | 42 | critical | — |
| Segurança | 80 | high | — |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-001 | 🔴 critical | architecture | 450 | O caminho de rejeição de token JWT expirado/malformado — o portão de autenticação de toda a API — nunca é exercitado por nenhum teste da suíte. |
| FIN-001 | 🟡 medium | finance | 250 | A página de orçamento reutiliza um componente cujos rótulos fixos descrevem o percentual como participação na renda, mas o valor exibido ali é participação no orçamento alocado — a matemática está correta, o rótulo mostrado ao usuário não é. |
| FIN-002 | 🔴 critical | finance | 180 | NetWorthSnapshotService duplica a lógica de custo de investimentos de PortfolioService mas sem o sinal buy/sell, inflando o patrimônio líquido persistido sempre que o usuário tiver registrado alguma venda. |
| SEC-001 | 🟠 high | security | 144 | apps/quebec-web's package-lock.json is stale and resolves nuxt/@nuxt/devtools to versions with multiple known high/critical CVEs (auth-bypass, SSR RCE, CPU exhaustion, and a critical unauthenticated dev-server RCE), while the sibling app klipper-web with the identical package.json semver range already resolves to a patched version. |
| ARCH-002 | 🟠 high | architecture | 112 | A lógica de validação e parsing de valores financeiros de useLancamentoForm — compartilhada pelos modais de novo e editar lançamento — não tem teste unitário dedicado. |
| SEC-002 | 🟢 low | security | 80 | The unauthenticated /api/v1/health endpoint returns Rails.env in its JSON body, letting any anonymous caller fingerprint whether the target is production/staging/development. |
| FIN-003 | 🔴 critical | finance | 54 | BankImport::AmountParser interpreta qualquer vírgula como decimal BR e corrompe silenciosamente valores no formato en-US (vírgula-milhar/ponto-decimal) vindos de CSV genérico, sem lançar erro nem ter teste que cubra o caso. |
| ARCH-003 | 🟠 high | architecture | 30 | A fórmula de patrimônio líquido (contas + investimentos) está duplicada entre NetWorthSnapshotService e ReportsController#net_worth em vez de reutilizar o service existente. |
| ARCH-004 | 🟡 medium | architecture | 16 | Quatro componentes Vue de entrada de dados financeiros (nova conta, novo membro, editar reembolso) não têm nenhuma cobertura de teste, direta ou indireta. |
| SEC-003 | 🟡 medium | security | 15 | Both frontend apps carry outdated transitive devDependencies (vite/esbuild dev-server, svgo image optimizer, vitest test runner, js-yaml/fast-uri) with published moderate/high advisories; none of these packages ship into the built production bundle, but they do run unpatched on every developer machine and CI job. |
| ARCH-005 | 🟡 medium | architecture | 10 | Cinco páginas centrais do Wealth OS (dashboard, contas, investimentos, orçamento, portadores) não têm nenhum teste de página. |
| ARCH-006 | 🟡 medium | architecture | 6 | ReportsController mistura dois padrões arquiteturais no mesmo arquivo: metade das actions agrega dados financeiros inline, a outra metade delega a Calculator services. |
