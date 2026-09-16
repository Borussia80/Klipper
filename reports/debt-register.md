# Registro de dívida técnica — Klipper

> Gerado automaticamente por `render-report.mjs` a partir de `reports/registry/findings.json`.
> Não editar manualmente — mudanças aqui serão sobrescritas na próxima execução.

| ID | Categoria | Descrição | Criado em | Última ocorrência | Impacto | Esforço | Prioridade |
|---|---|---|---|---|---|---|---|
| ARCH-001 | architecture | O caminho de rejeição de token JWT expirado/malformado — o portão de autenticação de toda a API — nunca é exercitado por nenhum teste da suíte. | 2026-09-16 | 2026-09-16 | 9 | 2 | 450 |
| FIN-001 | finance | A página de orçamento reutiliza um componente cujos rótulos fixos descrevem o percentual como participação na renda, mas o valor exibido ali é participação no orçamento alocado — a matemática está correta, o rótulo mostrado ao usuário não é. | 2026-09-16 | 2026-09-16 | 5 | 2 | 250 |
| FIN-002 | finance | NetWorthSnapshotService duplica a lógica de custo de investimentos de PortfolioService mas sem o sinal buy/sell, inflando o patrimônio líquido persistido sempre que o usuário tiver registrado alguma venda. | 2026-09-16 | 2026-09-16 | 9 | 2 | 180 |
| SEC-001 | security | apps/quebec-web's package-lock.json is stale and resolves nuxt/@nuxt/devtools to versions with multiple known high/critical CVEs (auth-bypass, SSR RCE, CPU exhaustion, and a critical unauthenticated dev-server RCE), while the sibling app klipper-web with the identical package.json semver range already resolves to a patched version. | 2026-09-16 | 2026-09-16 | 6 | 1 | 144 |
| ARCH-002 | architecture | A lógica de validação e parsing de valores financeiros de useLancamentoForm — compartilhada pelos modais de novo e editar lançamento — não tem teste unitário dedicado. | 2026-09-16 | 2026-09-16 | 7 | 3 | 112 |
| SEC-002 | security | The unauthenticated /api/v1/health endpoint returns Rails.env in its JSON body, letting any anonymous caller fingerprint whether the target is production/staging/development. | 2026-09-16 | 2026-09-16 | 2 | 1 | 80 |
| FIN-003 | finance | BankImport::AmountParser interpreta qualquer vírgula como decimal BR e corrompe silenciosamente valores no formato en-US (vírgula-milhar/ponto-decimal) vindos de CSV genérico, sem lançar erro nem ter teste que cubra o caso. | 2026-09-16 | 2026-09-16 | 9 | 3 | 54 |
| ARCH-003 | architecture | A fórmula de patrimônio líquido (contas + investimentos) está duplicada entre NetWorthSnapshotService e ReportsController#net_worth em vez de reutilizar o service existente. | 2026-09-16 | 2026-09-16 | 6 | 3 | 30 |
| ARCH-004 | architecture | Quatro componentes Vue de entrada de dados financeiros (nova conta, novo membro, editar reembolso) não têm nenhuma cobertura de teste, direta ou indireta. | 2026-09-16 | 2026-09-16 | 5 | 5 | 16 |
| SEC-003 | security | Both frontend apps carry outdated transitive devDependencies (vite/esbuild dev-server, svgo image optimizer, vitest test runner, js-yaml/fast-uri) with published moderate/high advisories; none of these packages ship into the built production bundle, but they do run unpatched on every developer machine and CI job. | 2026-09-16 | 2026-09-16 | 3 | 2 | 15 |
| ARCH-005 | architecture | Cinco páginas centrais do Wealth OS (dashboard, contas, investimentos, orçamento, portadores) não têm nenhum teste de página. | 2026-09-16 | 2026-09-16 | 4 | 6 | 10 |
| ARCH-006 | architecture | ReportsController mistura dois padrões arquiteturais no mesmo arquivo: metade das actions agrega dados financeiros inline, a outra metade delega a Calculator services. | 2026-09-16 | 2026-09-16 | 4 | 4 | 6 |
