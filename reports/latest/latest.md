# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `d0f0bff28d8fb98909e2bd32addffe154c98e6cb` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | critical |
| Segurança | medium |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| SEC-007 | 🟠 high | security | 324 | Os 5 agentes de auditoria completa (architecture/security/finance/runtime/ux) rodam automaticamente a cada merge no main com Bash irrestrito e um GITHUB_TOKEN de escrita (contents+pull-requests) no ambiente, enquanto leem o repositório inteiro sem nenhum gate contra conteúdo não-confiável — o mesmo padrão de risco (LLM01/prompt injection → ação com credencial de escrita) que `agent-pr-review.yml` já mitiga explicitamente para PRs de fork não existe aqui. |
| FIN-011 | 🔴 critical | finance | 144 | Excluir uma conta (soft-delete via `active: false`, feature nova de editar/excluir contas e portadores) não a remove do patrimônio líquido: NetWorthSnapshotService.compute e ReportsController#net_worth somam `user.accounts` sem o escopo `.active` já usado por AccountsController e DebtRankingCalculator, então o saldo da conta excluída continua inflando o patrimônio exibido em relatorios.vue e persistido mensalmente em net_worth_snapshots, divergindo do total mostrado em contas.vue — exatamente a classe de bug catalogada como FIN-002/ARCH-003 (saldo divergindo entre telas por lógica duplicada/inconsistente). |
| ARCH-011 | 🟡 medium | architecture | 105 | useModal (roteamento de todo modal financeiro, incluindo o fluxo de portadores recém-adicionado) e useToast (todo feedback de sucesso/erro do app) continuam sem teste direto. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded (natural_key já catalogado como FIN-001), então orcamento.vue, que mede proporção do orçamento (gasto/alocado), exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| ARCH-016 | 🟡 medium | architecture | 58.33 | O cabeçalho sticky de página (e o rótulo de seção uppercase) é reimplementado como string de inline-style idêntica em pelo menos 7 páginas (contas, portadores, orcamento, investimentos, transacoes, importar, relatorios); pages/portadores.vue, recém-adicionada no PR #165, perpetua o padrão em vez de extrair um componente. |
| ARCH-004 | 🟡 medium | architecture | 48 | De quatro componentes de modal financeiro sem cobertura, ModalNovaConta foi corrigido; ModalMount, ModalEditarReembolso e ModalNovoMembro (este último parte do fluxo novo de portadores) continuam com zero cobertura direta ou indireta. |
| ARCH-005 | 🟡 medium | architecture | 30 | Das quatro páginas centrais do Wealth OS sem teste de página identificadas anteriormente, dashboard.vue ganhou cobertura (dashboard.test.ts); contas, orçamento e a nova portadores.vue continuam sem nenhum teste de montagem/interação. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF continua sem poder ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído (natural_key já catalogado como FIN-008), quebrando o requisito de rastreabilidade da seção financeira. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell para posição líquida de investimentos, já documentada no model como causa de bug real anterior, permanece implementada de forma independente em três arquivos (model, portfolio_service, net_worth_snapshot_service) em vez de centralizada. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter continua propagando o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real (natural_key já catalogado como FIN-005), e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. Risco aceito e já documentado no próprio código, não uma regressão nova. |
| SEC-005 | 🟢 low | security | 18 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem rate limiting, enquanto create/sign_in/sign_up têm throttle explícito — mesma lacuna já catalogada em execuções anteriores. |
| SEC-003 | 🟢 low | security | 18 | `esbuild` (low, recorrente, sem fix publicado na faixa de nuxt atual) segue como a única advisory de dependência de frontend abaixo do portão de CI (`--audit-level=high` efetivo via audit-gate.mjs); `devalue`, citada na auditoria anterior, já foi resolvida. |
| SEC-006 | 🟢 low | security | 9.6 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly; a decisão arquitetural (aceitar o risco mitigado por CSP com nonce vs. migrar para cookie HttpOnly + cabeçalho CSRF) segue sem registro formal. |
| ARCH-015 | 🟢 low | architecture | 9 | A validação 'occurred_on não pode ser futuro' continua duplicada verbatim entre Transaction e Investment; qualquer ajuste de regra (ex: tolerância de timezone) precisa ser replicado manualmente nos dois lugares. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary continua usando 0.0 para 'sem base de cálculo' em pct_used (natural_key já catalogado como FIN-010), divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call; inalcançável via fluxo normal do app hoje (validação impede amount_limit <= 0), mas dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
