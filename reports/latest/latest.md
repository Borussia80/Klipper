# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `1936bd6b081cf6675cc7ec790ea65896722c7696` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | high |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | Sem mudança desde a última auditoria: useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem teste direto — open()/close()/reset de payload e o auto-dismiss via setTimeout nunca são exercitados isoladamente. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento) exibe um rótulo semanticamente errado para a métrica que de fato calcula; dashboard.vue, que de fato usa spentRatio = % da renda, é o único consumidor para o qual o rótulo é correto. |
| ARCH-009 | 🟡 medium | architecture | 56 | Sem mudança desde a última auditoria: o componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap, restauração de foco) continua sem cobertura própria. |
| ARCH-004 | 🟡 medium | architecture | 41.67 | Melhorou parcialmente: ModalNovaConta ganhou cobertura desde a última auditoria, mas ModalNovoMembro, ModalEditarReembolso e ModalMount continuam sem nenhum teste, direto ou indireto. |
| ARCH-005 | 🟡 medium | architecture | 31.25 | Melhorou parcialmente: dashboard ganhou teste de página desde a última auditoria, mas contas, orçamento e portadores — três das quatro páginas centrais do Wealth OS — continuam sem nenhum teste de página. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | Sem mudança desde a última auditoria: a regra de sinal buy/sell tem uma terceira reimplementação não coberta pelo teste de paridade existente, então uma mudança na regra pode divergir silenciosamente na validação de venda. |
| FIN-008 | 🟡 medium | finance | 18 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| SEC-003 | 🟢 low | security | 18 | `devalue` (moderate) e `esbuild` (low) continuam desatualizados nas dependências transitivas de dev de klipper-web e quebec-web, abaixo do limiar `--audit-level=high` do gate de CI (.github/workflows/ci.yml:119-121,170-172), então ambos ficam invisíveis ao portão automatizado. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | Sem mudança desde a última auditoria: os dois modais compartilham a lógica via useLancamentoForm, mas o template de apresentação e o CSS inteiro continuam duplicados entre os dois arquivos. |
| FIN-005 | 🟡 medium | finance | 9.6 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. |
| ARCH-014 | 🟡 medium | architecture | 9 | Sem mudança desde a última auditoria: o padrão visual de campo com select continua reimplementado em CSS scoped duplicado em pelo menos três modais de entidade diferentes dos de lançamento. |
| FIN-010 | 🟢 low | finance | 9 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; a validação do model impede amount_limit <= 0 no fluxo normal do app, mas dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-007 | 🟢 low | security | 7.2 | PasswordResetsController#create iguala o corpo da resposta para não vazar quais e-mails existem, mas não iguala o tempo de resposta: o envio de e-mail via SMTP síncrono (`deliver_now`) só acontece quando o usuário existe, criando um canal de timing para enumeração de e-mail — a mesma classe de problema que `AuthController#sign_in` já mitiga deliberadamente com `FAKE_PASSWORD_DIGEST` (apps/klipper-api/app/controllers/api/v1/auth_controller.rb:5-7), mas que não foi replicada aqui. |
| ARCH-015 | 🟢 low | architecture | 6 | Sem mudança desde a última auditoria: a regra 'occurred_on não pode ser futuro' continua duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar do diretório de concerns já existir no projeto para esse propósito. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha, apps/klipper-api/app/controllers/api/v1/password_resets_controller.rb:16-27) segue sem rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas. |
| SEC-006 | 🟢 low | security | 4.8 | O access token JWT da SPA continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural sobre aceitar esse risco residual (mitigado por CSP) ou migrar para cookie HttpOnly + CSRF segue sem resolução formal — o ADR está redigido mas não decidido. |
| FIN-004 | 🟢 low | finance | 1 | O bug antes catalogado como FIN-004 (hero do dashboard calculava spentRatio inline com fallback para 0, escondendo ciclo sem receita) não reproduz mais no código atual — dashboard.vue já reusa pctOfIncome() como o restante do arquivo. |
