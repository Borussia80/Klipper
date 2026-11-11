# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `e475071b8d9aee3f5a71b9b8318c5b2ab5cc2223` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | high |
| Domínio financeiro | medium |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam, pela segunda auditoria consecutiva, sem nenhum teste direto — open()/close()/reset de payload e o auto-dismiss via setTimeout só são exercitados incidentalmente através de mocks em testes de componentes individuais. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento) exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) não tem nenhuma cobertura de teste, direta ou indireta — a própria suíte de testes já documenta essa lacuna sem fechá-la. |
| ARCH-004 | 🟡 medium | architecture | 50 | Três componentes Vue de entrada/edição de dados financeiros (ModalNovoMembro, ModalEditarReembolso, ModalMount) continuam sem nenhuma cobertura de teste, direta ou indireta; ModalNovaConta, que fazia parte do mesmo grupo na auditoria anterior, já foi corrigido. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído — o AuditLog grava um evento agregado do lote (checksum, contagem), mas nenhuma transação individual referencia esse evento, e o fluxo de confirmação de PDF nem grava o checksum do arquivo original. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell, já causa documentada do bug real FIN-002 quando duplicada, tem uma terceira reimplementação em sufficient_quantity_for_sell não coberta pelo teste de paridade existente entre signed_cost e signed_cost_sql, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste de paridade acuse. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal da coluna de movimentação sem inversão com base numa suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal, deixando dado de patrimônio de importações BTG com risco não coberto de inversão silenciosa. |
| ARCH-005 | 🟢 low | architecture | 18 | Das quatro páginas centrais do Wealth OS sem teste de página na auditoria anterior (dashboard, contas, orçamento, portadores), três já ganharam cobertura; só portadores continua sem nenhum teste de página. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. |
| ARCH-014 | 🟡 medium | architecture | 9 | O padrão visual de campo com select (label, wrapper, seta customizada) é reimplementado em CSS scoped duplicado em pelo menos três modais de entidade diferentes dos de lançamento, então qualquer ajuste visual (ex: acessibilidade do caret, espaçamento) precisa ser replicado manualmente em cada arquivo e tende a divergir. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token continua sem rate limiting, inconsistente com as demais rotas de autenticação não-autenticadas (sign_in, sign_up, criação do reset) que já são throttled por IP. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é coberto por teste e inalcançável via fluxo normal do app (validação impede amount_limit <= 0), mas dado legado ou uma edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-003 | 🟢 low | security | 3.6 | apps/klipper-web e apps/quebec-web seguem em nuxt@3.21.11, dois minors atrás das versões que corrigem os CVEs moderate mais recentes do próprio pacote nuxt (não mais só devDependencies transitivas como devalue/esbuild); nenhum dos CVEs moderate é explorável no estado atual — klipper-web roda com `ssr: false` e nenhum dos dois apps usa server islands (`NuxtIsland`/`useHeadSafe`), e o `npm audit --audit-level=high` do CI (com exceções explícitas em audit-gate.mjs) já aceita moderate/low por decisão registrada em 2026-10-17 — mas a lacuna de versão em si continua crescendo. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA segue exposto a JavaScript via cookie não-httpOnly; a decisão arquitetural de aceitar esse risco (mitigado pela CSP com nonce em apps/klipper-web/server/middleware/csp.ts, que usa `script-src 'self' 'nonce-...'` em produção) ou migrar para cookie HttpOnly + CSRF continua sem resolução formal. |
