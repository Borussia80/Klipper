# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `2426986033d2e4414685719d65f289876e573546` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | high |
| Domínio financeiro | medium |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 252 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — inalterado desde a última auditoria. |
| ARCH-016 | 🟠 high | architecture | 147 | O limiar que decide se uma categoria de orçamento está 'ESTOURADO' e o valor de excedente (overshoot) mostrado ao usuário são calculados dentro de BudgetCategoryCard.vue e não são exercitados por nenhum teste, direto ou indireto — violação da Regra de Ouro (cálculo financeiro sem teste) ainda não catalogada em registry. |
| ARCH-009 | 🟡 medium | architecture | 120 | O componente-base compartilhado por todos os modais do app continua sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-004 | 🟡 medium | architecture | 72 | Três dos quatro componentes de entrada/edição financeira já flagueados (ModalNovoMembro, ModalEditarReembolso, ModalMount) continuam sem cobertura; ModalNovaConta foi corrigido desde a última execução — tendência de melhora parcial, não resolução completa. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento alocado) exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| ARCH-005 | 🟡 medium | architecture | 41.67 | Duas das quatro páginas centrais do Wealth OS originalmente flagueadas (dashboard, orçamento) ganharam teste de página; contas e portadores continuam sem nenhum — tendência de melhora parcial. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| ARCH-013 | 🟡 medium | architecture | 28 | A lógica de sinal buy/sell tem uma terceira reimplementação (no cálculo de posição para validar venda) não coberta pelo teste de paridade existente, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. |
| ARCH-008 | 🟡 medium | architecture | 12 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped continuam duplicados quase byte a byte entre os dois arquivos. |
| ARCH-014 | 🟡 medium | architecture | 9 | O padrão visual de campo com select (label, wrapper, seta customizada) continua reimplementado em CSS scoped duplicado em pelo menos três modais de entidade. |
| ARCH-015 | 🟢 low | architecture | 8 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem rate limiting; a única regra de throttle da feature cobre o POST que gera o token, não o PATCH que o consome, permitindo tentativas ilimitadas de adivinhar/forçar um token de reset válido. |
| SEC-003 | 🟢 low | security | 5.4 | A dependência de produção `nuxt` (3.21.11) segue desatualizada em ambos os frontends, com 3 advisories públicos (2 moderate, 1 low), substituindo o pacote `devalue` da auditoria anterior como a flag dominante do npm audit; nenhuma pré-condição de exploração (server islands, routeRules, pages desabilitado) foi encontrada no código atual, e o lado Ruby segue não verificável neste ambiente por falta de bundler/brakeman instalados. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é coberto por teste e inalcançável via fluxo normal do app (validação impede amount_limit <= 0), mas dado legado ou uma edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural de aceitar esse risco (mitigado por CSP com nonce) ou migrar para cookie HttpOnly + CSRF segue formalmente pendente — o ADR-2026-09-17-003 existe e documenta a assimetria, mas permanece em `proposed/`, não `accepted/`. |
