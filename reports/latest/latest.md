# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `8f7b1174b8586927200ef1b158932cea1d745c00` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | medium |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — open()/close()/auto-dismiss só são exercitados incidentalmente via mocks em testes de componentes individuais; sem mudança desde a última auditoria. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda', então orcamento.vue (que mede % do orçamento alocado, não da renda) exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) continua sem nenhuma cobertura de teste, direta ou indireta — sem mudança desde a última auditoria. |
| ARCH-004 | 🟡 medium | architecture | 40 | Dos quatro componentes de entrada/edição de dados financeiros sem cobertura apontados na auditoria anterior, ModalNovaConta foi corrigido (ganhou teste de montagem); ModalNovoMembro, ModalEditarReembolso e ModalMount continuam com zero cobertura. |
| ARCH-005 | 🟡 medium | architecture | 30 | Das quatro páginas centrais do Wealth OS sem teste de página apontadas na auditoria anterior, dashboard foi corrigido; contas, orçamento e portadores continuam sem nenhum teste de página. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell tem uma terceira reimplementação em sufficient_quantity_for_sell não coberta pelo teste de paridade entre signed_cost e signed_cost_sql, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda. Sem mudança desde a última auditoria. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. |
| SEC-007 | 🟢 low | security | 12 | POST /api/v1/password_resets devolve o mesmo corpo de resposta para e-mail existente ou não, mas só o ramo existente aguarda um envio de e-mail via SMTP síncrono (deliver_now), criando uma diferença de latência observável que permite enumerar contas cadastradas por timing mesmo com a mensagem uniforme. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica via useLancamentoForm, mas o template e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. Sem mudança desde a última auditoria. |
| ARCH-014 | 🟢 low | architecture | 9 | O padrão visual de campo com select (wrapper, seta customizada, appearance:none) é reimplementado em CSS scoped duplicado em pelo menos cinco modais de entidade diferentes, então qualquer ajuste visual precisa ser replicado manualmente em cada arquivo. Sem mudança desde a última auditoria. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. Sem mudança desde a última auditoria. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é inalcançável via fluxo normal do app (validação impede amount_limit <= 0), mas dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural de aceitar esse risco (mitigado pela CSP com nonce) ou migrar para cookie HttpOnly + CSRF segue sem resolução formal. |
