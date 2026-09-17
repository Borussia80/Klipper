# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `75004f142b7c0abc4bc87028941c372bd2fb1af6` · **Modo:** fast

> ⚠️ **Relatório incompleto.** As análises de **architecture**, **security** não produziram resultado neste run. O que segue abaixo cobre só 1 das 3 seções esperadas — ausência de finding numa área não avaliada não significa ausência de problema.

## Seções

| Seção | Risco |
|---|---|
| Domínio financeiro | high |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| FIN-004 | 🔴 critical | finance | 288 | O hero do dashboard ainda devolve 0 (em vez de null) quando não há receita no ciclo, fazendo InstrumentReadout desenhar a barra 'dentro da faixa' preenchida em 0% como se fosse gasto medido, e não a ausência de dado — o mesmo defeito catalogado em FIN-004 continua sem correção no código atual. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' e o estado nulo genérico ('Sem orçamento definido') hardcoded no componente, então orcamento.vue (que mede proporção do orçamento, não de renda) exibe um rótulo semanticamente errado para a métrica que realmente calcula. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o item de rastreabilidade exigido pela seção financeira do escopo de auditoria. |
| FIN-005 | 🔴 critical | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição que o próprio autor documenta como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. |
