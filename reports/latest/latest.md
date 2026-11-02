# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `e26deea9dac393f80529c4ba0396f2fabbbf342c` · **Modo:** fast

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
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento gasto, não da renda) exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) não tem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-004 | 🟡 medium | architecture | 33.33 | Três componentes Vue de entrada/edição de dados financeiros (ModalNovoMembro, ModalEditarReembolso, ModalMount) continuam sem nenhuma cobertura de teste, direta ou indireta; o quarto componente da lista anterior (ModalNovaConta) já foi corrigido. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell (documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada) tem uma terceira reimplementação em sufficient_quantity_for_sell, não coberta pelo teste de paridade existente entre signed_cost e signed_cost_sql, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste de paridade acuse. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. |
| ARCH-005 | 🟡 medium | architecture | 12 | Das quatro páginas centrais do Wealth OS apontadas na auditoria anterior (dashboard, contas, orçamento, portadores), três já ganharam teste de página; só portadores.vue continua sem nenhum teste de página. |
| SEC-003 | 🟢 low | security | 10.8 | Dependências transitivas de dev/build de ambos os frontends seguem com avisos moderate/low não corrigidos — agora incluindo o próprio `nuxt` (CVE de route rules case-insensitive) além do `esbuild` recorrente — e o lado Ruby da auditoria continua bloqueado por falta de acesso à rede nesta sandbox. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o bloco inteiro de CSS scoped (menos o trecho exclusivo de descarte de rascunho) continua duplicado quase byte a byte entre os dois arquivos, embora o template de apresentação já tenha divergido mais do que no registro anterior. |
| ARCH-014 | 🟡 medium | architecture | 9 | O padrão visual de campo com select (wrapper relativo + seta customizada) continua reimplementado em CSS scoped byte-idêntico em pelo menos três modais de entidade (ModalNovaConta, ModalEditarReembolso, ModalNovoMembro), agora sob as classes .sel-wrap/.sel-caret/.fi-sel, então qualquer ajuste visual (ex: acessibilidade do caret, espaçamento) precisa ser replicado manualmente em cada arquivo e tende a divergir. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token, o endpoint que redime o token de reset de senha, continua sem nenhum rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas (sign_in, sign_up, criação do reset). |
| ARCH-016 | 🟢 low | architecture | 5.33 | O conjunto de rotas, labels e ícones da navegação principal é mantido em duas representações independentes sem fonte única — markup inline em AppSidebar.vue e um array de dados em MobileNav.vue — e já divergiram em ordem e em desenho de ícone para a mesma rota, então adicionar/renomear uma página exige editar os dois arquivos manualmente. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é coberto por teste e inalcançável via fluxo normal do app (validação impede amount_limit <= 0), mas dado legado ou uma edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 2 | O token de acesso JWT da SPA segue acessível a qualquer script executado na página (cookie não-HttpOnly), e a ADR que deveria decidir entre aceitar esse risco (mitigado por CSP com nonce) ou migrar para HttpOnly+CSRF continua sem resolução formal. |
