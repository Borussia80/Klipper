# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `9a4bca723c292713c16f377a388e74912be9655a` · **Modo:** fast

> ⚠️ **Relatório incompleto.** A análise de **security** não produziu resultado neste run. O que segue abaixo cobre só 2 das 3 seções esperadas — ausência de finding numa área não avaliada não significa ausência de problema.

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | high |
| Domínio financeiro | medium |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 216 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto, sem melhora desde a última auditoria. |
| ARCH-009 | 🟡 medium | architecture | 93.33 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) continua sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-004 | 🟡 medium | architecture | 84 | Três componentes Vue de entrada/edição de dados financeiros (ModalNovoMembro, ModalEditarReembolso, ModalMount) continuam sem nenhuma cobertura de teste; ModalNovaConta foi corrigido desde a última auditoria. |
| ARCH-005 | 🟡 medium | architecture | 70 | Três páginas centrais do Wealth OS (contas, orçamento, portadores) continuam sem nenhum teste de página; dashboard foi corrigido desde a última auditoria, mostrando progresso parcial. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo "% da renda" hardcoded, então orcamento.vue (que mede % do orçamento consumido, não % da renda) exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não consegue ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela ou endpoint — a trilha de auditoria (audit_logs) registra o evento de import em agregado, não o vínculo por transação. |
| ARCH-013 | 🟡 medium | architecture | 24 | A lógica de sinal buy/sell tem uma terceira reimplementação em sufficient_quantity_for_sell não coberta pelo teste de paridade existente, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste acuse. |
| FIN-010 | 🟢 low | finance | 24 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' (amount_limit <= 0) em pct_used, divergindo da convenção nil já adotada em PortfolioService e ReimbursementCoverageCalculator para o mesmo tipo de ausência de base — uma categoria sem orçamento definido mas com gasto lançado (spent > 0, amount_limit = 0) recebe o mesmo pct_used (0.0) de uma categoria realmente zerada. |
| FIN-005 | 🟡 medium | finance | 21 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum exemplo real de débito, e a suíte de teste não cobre esse caso — se a suposição estiver errada, débitos dessa conta importam com sinal trocado sem nenhum alerta. |
| ARCH-008 | 🟡 medium | architecture | 20 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados entre os dois arquivos. |
| ARCH-014 | 🟡 medium | architecture | 12 | O padrão visual de campo com select é reimplementado em CSS scoped duplicado em pelo menos quatro modais de entidade diferentes dos de lançamento, então qualquer ajuste visual precisa ser replicado manualmente em cada arquivo. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado. |
