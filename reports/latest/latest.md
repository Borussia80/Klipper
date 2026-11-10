# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `f0de64af202bf70787e6285c0d5385978c628616` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | medium |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — open()/close()/reset de payload e o auto-dismiss via setTimeout só são exercitados incidentalmente através de mocks em testes de componentes individuais. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento) exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap via useFocusTrap e restauração de foco ao gatilho) não tem nenhuma cobertura de teste, direta ou indireta — e isso agora está documentado explicitamente no próprio arquivo de testes de stress dos modais, que lista esse gap como fora do seu escopo. |
| ARCH-004 | 🟡 medium | architecture | 33.33 | Três componentes Vue de entrada/edição de dados financeiros (ModalNovoMembro, ModalEditarReembolso, ModalMount) continuam sem nenhuma cobertura de teste, direta ou indireta. ModalNovaConta, que fazia parte deste mesmo finding na auditoria anterior, já foi corrigido. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell (documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada) tem uma terceira reimplementação em sufficient_quantity_for_sell não coberta pelo teste de paridade existente entre signed_cost e signed_cost_sql, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste de paridade acuse. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. |
| SEC-003 | 🟢 low | security | 18 | Ambos os frontends (klipper-web, quebec-web) seguem com dependências de build desatualizadas gerando avisos moderate/low no npm audit, sem versão corrigida publicada para a maioria (nuxt 4.6.x, esbuild), e o portão de CI (audit-gate.mjs) aceita isso deliberadamente por não haver fix disponível. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas a quase totalidade do CSS scoped (146 das 161 linhas) continua duplicada entre os dois arquivos; o template de apresentação divergiu mais desde a última auditoria por conta de features exclusivas do modo criação (descarte de rascunho, conta de destino), mas isso reforça a necessidade de isolar o que é genuinamente comum. |
| ARCH-014 | 🟡 medium | architecture | 9 | O padrão visual de campo com select (classes .fi/.fi-sel/.sel-wrap: label, wrapper, seta customizada) é reimplementado em CSS scoped duplicado em pelo menos três modais de entidade diferentes dos de lançamento (ModalNovaConta, ModalNovoMembro, ModalEditarReembolso), então qualquer ajuste visual precisa ser replicado manualmente em cada arquivo e tende a divergir. |
| ARCH-005 | 🟢 low | architecture | 6 | Das quatro páginas centrais do Wealth OS sem teste na auditoria anterior (dashboard, contas, orçamento, portadores), três já foram corrigidas (dashboard.test.ts, contas.test.ts, orcamento.test.ts); resta apenas portadores.vue sem nenhum teste de página. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto (hoje vazio, só com .keep) para esse propósito. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, ao contrário das demais rotas de autenticação não-autenticadas. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é inalcançável via fluxo normal do app (validação do model impede amount_limit <= 0), mas dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly (`klipper_token`), e a decisão arquitetural de aceitar esse risco ou migrar para cookie HttpOnly segue sem resolução formal — o ADR correspondente permanece em `proposed`. |
