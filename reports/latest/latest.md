# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `2fdeeea114a6f3bea01235b2b71d12b25cbd212e` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | medium |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — sem mudança desde a última auditoria. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo da razão hardcoded como '% da renda', então orcamento.vue (que mede proporção do orçamento gasto, não da renda) exibe um rótulo semanticamente errado para o número que de fato calcula. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape, focus trap, restauração de foco) continua sem cobertura de teste direta ou indireta — sem mudança desde a última auditoria. |
| SEC-007 | 🟢 low | security | 45 | A allowlist de Host (`config.hosts`) tem fallback fail-open (sem restrição) quando a env var RAILS_ALLOWED_HOSTS não está definida, em vez de fail-closed ou de uma verificação em boot que impeça o deploy sem o valor configurado — o próprio código documenta essa troca de responsabilidade para o operador, mas não há nenhum mecanismo no repositório que garanta que o painel do Render de fato tenha o valor definido. |
| ARCH-004 | 🟡 medium | architecture | 40 | Três dos quatro componentes Vue de entrada/edição de dados financeiros continuam sem nenhuma cobertura de teste (melhora parcial: ModalNovaConta ganhou teste desde a última auditoria). |
| ARCH-005 | 🟡 medium | architecture | 40 | Três das quatro páginas centrais do Wealth OS (contas, orçamento, portadores) continuam sem teste de página; dashboard foi corrigido desde a última auditoria. |
| ARCH-016 | 🟡 medium | architecture | 30 | CategoryMergeService e a hierarquia de duas camadas (Category#parent/children) estão implementados e cobertos por spec de model/service, mas não têm nenhum ponto de entrada HTTP: não existe rota POST /categories/:id/merge, e create/update de categoria não aceita parent_id — então a funcionalidade inteira desta fatia é inacessível a qualquer cliente (web ou script) fora do console/specs Rails. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído — não existe FK nem campo de proveniência em `transactions`, só um log agregado do evento de import (`audit_logs`), que não referencia as linhas individuais. Isso quebra o requisito de rastreabilidade da seção financeira. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell tem uma terceira reimplementação (em sufficient_quantity_for_sell) fora do teste de paridade existente entre signed_cost e signed_cost_sql — sem mudança desde a última auditoria. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição explicitamente documentada como não verificada contra nenhum débito real, e nenhum teste trava o sinal esperado para esse caso — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal caso a suposição esteja errada. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento continuam com o template de apresentação e o CSS scoped inteiro duplicados quase byte a byte, apesar de já compartilharem a lógica via useLancamentoForm — sem mudança desde a última auditoria. |
| ARCH-014 | 🟡 medium | architecture | 9 | O padrão visual de campo com select continua reimplementado em CSS scoped duplicado em pelo menos quatro modais de entidade diferentes dos de lançamento. |
| SEC-003 | 🟢 low | security | 8 | O chain de dependências transitivas do Nuxt 3.21.x em ambos os frontends carrega duas advisories `high` (braces DoS, node-forge RSA signature bypass) sem fix publicado além de uma major bump para Nuxt 4; o risco já foi triado e aceito via gate de CI documentado e auto-expirável, mas a causa raiz (dependência presa em Nuxt 3) continua sem correção definitiva. |
| SEC-006 | 🟢 low | security | 8 | A decisão arquitetural de aceitar a exposição do access token da SPA a JavaScript (mitigada por CSP com nonce) continua sem resolução formal: o ADR-2026-09-17-003 segue `proposed`, não `accepted` nem `rejected`. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' continua duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado — sem mudança desde a última auditoria. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas — mesmo finding de SEC-005 em auditorias anteriores, sem alteração no código. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido. O caminho é coberto por teste e hoje inalcançável via fluxo normal do app (validação de Budget impede amount_limit <= 0 na criação), mas dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite — o mesmo padrão de ambiguidade já corrigido em FIN-007/FIN-009, reintroduzido aqui. |
