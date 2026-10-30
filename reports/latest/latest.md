# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `2399acb4d3eab3f10806ebdd0bf32e7a5365b78c` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | medium |
| Segurança | medium |

## Possible Regressions

- **SEC-003** — low → medium: `npm audit --json` em apps/klipper-web (29/30-10-2026): `seroval` moderate (via nuxt, CWE-79/94, GHSA-f86p-h4j2-7qgj e GHSA-9wx9-5pv9-3349, range 1.5.5-1.6.10, `fixAvailable: true` sem major bump), `esbuild` low (GHSA-g7r4-m6w7-qqqr, range >=0.27.3 <0.28.1, `fixAvailable: true`), e mais 4 avisos low sem correção publicada (`@rollup/plugin-node-resolve`, `deepmerge`, `vite-plugin-pwa`/`@vite-pwa/nuxt`, `workbox-build`, todos transitivos de `nitropack`/`@vite-pwa/nuxt`). `devalue` (moderate na auditoria anterior) não aparece mais no audit — já resolvido upstream. O portão de CI (`.github/scripts/audit-gate.mjs:13`) só bloqueia high/critical por desenho, então nada disso falha o PR.

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — open()/close()/reset de payload e o auto-dismiss via setTimeout só são exercitados incidentalmente através de mocks em testes de componentes individuais. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo '% da renda' hardcoded no template, então o hero de orcamento.vue exibe esse rótulo para uma razão que na verdade mede gasto sobre orçamento alocado, não renda. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) continua sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-004 | 🟡 medium | architecture | 50 | Três componentes Vue de entrada/edição de dados financeiros (ModalNovoMembro, ModalEditarReembolso, ModalMount) continuam sem nenhuma cobertura de teste, direta ou indireta — ModalNovaConta, o quarto componente apontado na última auditoria, já foi corrigido. |
| ARCH-005 | 🟡 medium | architecture | 33.33 | Duas páginas centrais do Wealth OS (contas, portadores) continuam sem nenhum teste de página — dashboard e orçamento, as outras duas apontadas na última auditoria, já foram corrigidas. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF continua sem referência persistida ao arquivo/lote de origem, então não há como rastreá-la de volta à importação depois que o import é concluído. |
| SEC-003 | 🟡 medium | security | 27 | O cluster de dependências de build/dev transitivas de klipper-web e quebec-web segue com avisos abaixo do portão de CI; o `devalue` da última auditoria foi corrigido, mas `seroval` (moderate, veio junto com o próprio nuxt) e `esbuild` (low) têm correção não-major disponível e não foi aplicada. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell (documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada) tem uma terceira reimplementação não coberta pelo teste de paridade existente, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste de paridade acuse. |
| ARCH-016 | 🟡 medium | architecture | 20 | A lógica de agrupamento de linhas por portador de cartão e atribuição de membro por grupo no fluxo de importação de fatura multi-titular vive inline em pages/importar.vue (fora de useImport.ts) e não tem nenhuma cobertura de teste direta — um erro na atribuição de portador numa fatura com múltiplos titulares não seria pego por nenhum teste existente. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG continua com risco não coberto de inversão silenciosa de sinal. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. |
| ARCH-014 | 🟡 medium | architecture | 9 | O padrão visual de campo com select (classe utilitária `.fi-sel`, wrapper e seta customizada) é reimplementado em CSS scoped duplicado em pelo menos três modais de entidade diferentes dos de lançamento, então qualquer ajuste visual (ex: acessibilidade do caret, espaçamento) precisa ser replicado manualmente em cada arquivo e tende a divergir. |
| SEC-007 | 🟡 medium | security | 6.67 | O pacote `nuxt` (dependência direta, não transitiva) está travado em 3.21.11 em klipper-web e quebec-web, com duas CVEs moderate e uma low sem correção publicada na série 3.x — subir exige salto de major version para 4.6.3, mas o risco real hoje é baixo porque nenhum dos apps usa Server Islands e nenhum `useHead`/`useSeoMeta` recebe conteúdo vindo do usuário. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, permitindo força bruta do token por IP sem limite. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary continua usando 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é coberto por teste e inalcançável via fluxo normal do app (validação impede amount_limit <= 0), mas dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA (15 min de validade) continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural de aceitar esse risco (mitigado pela CSP com nonce) ou migrar para cookie HttpOnly + CSRF segue sem resolução formal no ADR. |
