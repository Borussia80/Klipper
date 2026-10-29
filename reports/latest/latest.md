# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `23ebd1885cb676c2876d71913b90855852e36058` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | high |
| Domínio financeiro | critical |
| Segurança | low |

## Possible Regressions

- **ARCH-013** — medium → critical: apps/klipper-api/app/models/investment.rb:38 (`signed_cost_sql`), :43 (`signed_cost`) e :70-75 (`sufficient_quantity_for_sell`, que recalcula o sinal buy/sell de forma independente com `i.operation_type == "sell" ? -i.quantity : i.quantity`). O teste de paridade em spec/models/investment_spec.rb:102-112 compara apenas `signed_cost` com `signed_cost_sql` — nunca exercita a terceira implementação de `sufficient_quantity_for_sell`. O próprio comentário em investment.rb:32-37 documenta que essa duplicação de sinal já causou o bug real FIN-002 (saldo de patrimônio inflado em duas vezes o valor de cada venda) quando só havia duas implementações.

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — open()/close()/reset de payload e o auto-dismiss via setTimeout só são exercitados incidentalmente através de mocks em testes de componentes individuais. |
| FIN-011 | 🔴 critical | finance | 105 | orcamento.vue monta o hero 'Livre no ciclo' e os cards 'Alocado'/'Gasto' somando amount_limit e spent de todas as linhas de BudgetEngine#summary (pai + filha), duplicando o limite e o gasto de qualquer categoria com sub-orçamento, em vez de usar BudgetEngine#totals — já implementado e testado no backend para evitar exatamente essa duplicação, mas nunca exposto por uma rota nem consumido pelo frontend. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento alocado) exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) não tem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-004 | 🟡 medium | architecture | 33.33 | Desde a última auditoria, ModalNovaConta ganhou cobertura de teste, mas ModalNovoMembro, ModalEditarReembolso e ModalMount — que monta e roteia todos os modais financeiros via useModal — continuam sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-005 | 🟡 medium | architecture | 33.33 | Desde a última auditoria, dashboard e orçamento ganharam testes de página, mas contas e portadores — duas páginas centrais do Wealth OS — continuam sem nenhum teste de página. |
| ARCH-013 | 🔴 critical | architecture | 30 | A regra de sinal buy/sell tem uma terceira reimplementação em sufficient_quantity_for_sell não coberta pelo teste de paridade existente, então uma mudança futura na regra de sinal pode divergir silenciosamente na validação de venda (permitindo vender mais do que a posição real, ou bloqueando vendas válidas) sem que nenhum teste acuse — exatamente o padrão de cálculo financeiro sem teste que a Regra de Ouro do projeto trata como crítico por padrão. |
| FIN-008 | 🟡 medium | finance | 24 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois da importação — não há coluna de proveniência no schema nem exibição na UI. |
| FIN-010 | 🟢 low | finance | 24 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService e ReimbursementCoverageCalculator para o mesmo tipo de proporção sem base válida. |
| FIN-012 | 🟢 low | finance | 18 | O chip de reembolso no dashboard mistura coverage_pct mensal com o sinal alert (que é acumulado de 3 meses) sem indicar a diferença de escala ao usuário — ambiguidade visual já catalogada no ROADMAP, matemática correta mas leitura enganosa, ainda sem a correção descrita no próprio ROADMAP. |
| ARCH-014 | 🟡 medium | architecture | 15 | O padrão visual de campo com select (label, wrapper, seta customizada) continua reimplementado em CSS scoped duplicado em pelo menos quatro arquivos diferentes dos de lançamento (e numa quinta variante com os mesmos nomes de classe mas CSS distinto em dashboard.vue), então qualquer ajuste visual (ex: acessibilidade do caret, espaçamento) precisa ser replicado manualmente e tende a divergir ainda mais à medida que o app cresce. |
| FIN-005 | 🟡 medium | finance | 12 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum spec exercita um lançamento de débito desse extrato para confirmar o sinal. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, permitindo tentativas ilimitadas de adivinhar o token por IP. |
| SEC-003 | 🟢 low | security | 3.6 | Dependências transitivas de build/dev do Nuxt 3.21 em klipper-web e quebec-web seguem com avisos moderate/low sem correção fora de uma major para Nuxt 4; o lado Rails continua sendo um ponto cego total de auditoria automatizada neste ambiente, sem bundler/brakeman disponíveis. |
| SEC-006 | 🟢 low | security | 2 | A decisão arquitetural sobre o access token do SPA em cookie legível por JavaScript (ADR-2026-09-17-003) segue sem resolução formal — nem aceita com a mitigação documentada, nem superada por uma migração para HttpOnly + CSRF. |
