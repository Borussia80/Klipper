# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `c7277cb55376b50061bd363af821507e3e94dbd8` · **Modo:** fast

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
| ARCH-004 | 🟡 medium | architecture | 60 | Quatro componentes Vue de entrada/edição de dados financeiros continuam sem nenhuma cobertura de teste, direta ou indireta. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo '% da renda' hardcoded no template, então orcamento.vue exibe um rótulo semanticamente errado para a razão que de fato calcula (% do orçamento consumido). |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) não tem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-005 | 🟡 medium | architecture | 33.33 | Das quatro páginas centrais do Wealth OS sem teste de página apontadas na auditoria anterior, dashboard já ganhou cobertura própria (dashboard.test.ts); contas, orçamento e portadores continuam sem nenhum teste de página. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell (documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada) tem uma terceira reimplementação não coberta pelo teste de paridade existente entre signed_cost e signed_cost_sql, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste de paridade acuse. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. |
| SEC-003 | 🟢 low | security | 18 | `devalue` (moderate, DoS via entrada malformada) e `esbuild` (low, leitura arbitrária de arquivo no dev server) seguem desatualizados em devDependencies transitivas de klipper-web/quebec-web; nenhum CVE encontrado no lado Ruby (bundler-audit limpo). |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. |
| ARCH-014 | 🟡 medium | architecture | 9 | O padrão visual de campo com select (label, wrapper, seta customizada) é reimplementado em CSS scoped duplicado em pelo menos três modais de entidade diferentes dos de lançamento, então qualquer ajuste visual (ex: acessibilidade do caret, espaçamento) precisa ser replicado manualmente em cada arquivo e tende a divergir. |
| ARCH-016 | 🟢 low | architecture | 9 | ImportsController repete verbatim, entre as actions create e confirm, tanto a validação de account_id obrigatório quanto o cálculo de status de importação (success/failure a partir de imported+duplicates+errors), sem extrair nenhum dos dois para um método privado compartilhado. |
| ARCH-017 | 🟢 low | architecture | 9 | uploadFile e previewFile em useImport duplicam quase por completo o boilerplate de estado de loading/erro e montagem de FormData, em vez de compartilhar uma função interna parametrizada por endpoint e ref de destino. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, ao contrário das demais rotas de autenticação não-autenticadas. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é inalcançável via fluxo normal do app (validação de Budget impede amount_limit <= 0), mas dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural de aceitar esse risco (mitigado pela CSP com nonce) ou migrar para cookie HttpOnly + CSRF segue sem resolução formal — o ADR permanece `proposed`. |
