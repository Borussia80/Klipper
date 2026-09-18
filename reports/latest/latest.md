# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `7410d748d7be70d68e0451c3b07d98019c668da4` · **Modo:** fast

> ⚠️ **Relatório incompleto.** A análise de **security** não produziu resultado neste run. O que segue abaixo cobre só 2 das 3 seções esperadas — ausência de finding numa área não avaliada não significa ausência de problema.

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | medium |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem teste direto, e o número de consumidores diretos aumentou desde a última auditoria (agora inclui BudgetCategoryCard.vue). |
| ARCH-004 | 🟡 medium | architecture | 60 | Quatro componentes Vue de entrada/edição de dados financeiros — incluindo ModalMount.vue, o switchboard que decide qual modal financeiro é montado com base em useModal — continuam sem nenhuma cobertura de teste, direta ou indireta. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded no template, então orcamento.vue exibe esse rótulo semanticamente errado para a métrica que de fato mede (% do orçamento alocado), enquanto o número em si está correto. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) não tem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-005 | 🟡 medium | architecture | 48 | Das quatro páginas centrais do Wealth OS sem teste de página apontadas na auditoria anterior, dashboard já foi corrigida; contas, orçamento e portadores continuam sem nenhum teste de página. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell tem uma terceira reimplementação (dentro de sufficient_quantity_for_sell) não coberta pelo teste de paridade existente entre signed_cost e signed_cost_sql, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste de paridade acuse. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal caso o formato real de débito divirja da suposição. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. |
| ARCH-014 | 🟡 medium | architecture | 9 | O padrão visual de campo com select (label, wrapper, seta customizada) é reimplementado em CSS scoped duplicado em pelo menos cinco modais de entidade diferentes, então qualquer ajuste visual (ex: acessibilidade do caret, espaçamento) precisa ser replicado manualmente em cada arquivo e tende a divergir. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido — validação atual do modelo Budget impede amount_limit <= 0 no fluxo normal do app (Evidence unavailable sobre se algum caminho de dado legado ou edição direta na base ainda alcança amount_limit <= 0), mas caso alcance, o card de orçamento mostraria '0% usado' em vez de sinalizar ausência de limite. |
