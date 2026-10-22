# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `ff373f5c7b8cb8ff1ce8e4f9af5011e19a125e8b` · **Modo:** fast

> ⚠️ **Relatório incompleto.** A análise de **security** não produziu resultado neste run. O que segue abaixo cobre só 2 das 3 seções esperadas — ausência de finding numa área não avaliada não significa ausência de problema.

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | medium |

## Possible Regressions

- **ARCH-004** — medium → high: apps/klipper-web/components/ui/ModalNovaConta.vue, ModalNovoMembro.vue, ModalEditarReembolso.vue — nenhum arquivo correspondente em apps/klipper-web/components/ui/__tests__/ (listagem completa do diretório confirma apenas ModalConfirmDelete, ModalEditarCartao, ModalEditarLancamento, ModalNovaCategoria, ModalNovoAporte, ModalNovoLancamento com testes)

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-009 | 🟡 medium | architecture | 80 | BaseModal.vue, componente compartilhado por praticamente todos os modais do app (ESC, clique no backdrop, focus trap via useFocusTrap, restauração de foco), continua sem nenhum teste direto ou indireto. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo '% da renda' hardcoded no template, então orcamento.vue exibe um rótulo semanticamente incorreto para a métrica de gasto-sobre-orçamento que de fato calcula. |
| ARCH-011 | 🟡 medium | architecture | 48 | Os dois composables singleton que controlam qual modal financeiro está aberto e qual toast é exibido em todo o app continuam sem teste unitário direto. |
| ARCH-004 | 🟠 high | architecture | 37.5 | Três modais de entrada/edição de dados financeiros (nova conta, novo portador/membro, editar vínculo de reembolso) continuam sem nenhuma cobertura de teste, reduzido de quatro para três desde a última auditoria. |
| ARCH-005 | 🟡 medium | architecture | 31.25 | A página dashboard ganhou teste desde a última auditoria, mas contas, orçamento e portadores continuam sem nenhum teste de página. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira (toda transação precisa ser rastreável até sua origem). |
| FIN-005 | 🟡 medium | finance | 11.2 | BtgExtratoAdapter propaga o sinal de débito/crédito de extrato BTG a partir de uma suposição documentada como não verificada, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal caso a suposição esteja errada. |
| ARCH-015 | 🟢 low | architecture | 9 | A regra 'occurred_on não pode ser futuro' está implementada duas vezes, de forma independente, em Investment e Transaction, sem concern compartilhado para mantê-las sincronizadas. |
| ARCH-016 | 🟡 medium | architecture | 8 | O backend implementa e testa uma capacidade de cotação ao vivo (endpoint de quotes + métodos current_value/gain_loss em Investment), mas nada no frontend chama esse endpoint e nenhum service/controller alimenta o current_price necessário, deixando a funcionalidade órfã. |
| ARCH-014 | 🟢 low | architecture | 8 | O padrão visual de campo select com seta customizada é copiado como CSS scoped em pelo menos 4 componentes de modal em vez de ser um componente/estilo compartilhado. |
| ARCH-008 | 🟢 low | architecture | 5.4 | Os modais de criar e editar 'lançamento' compartilham lógica de formulário via composable mas duplicam integralmente template e CSS. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é coberto por teste e inalcançável via fluxo normal do app (validação de Budget impede amount_limit <= 0), mas dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| FIN-004 | 🟢 low | finance | 1 | O bug histórico do hero do dashboard (spentRatio com fallback para 0 em vez de null quando não há receita) já foi corrigido — dashboard.vue agora reusa pctOfIncome, que retorna null nesse caso. |
