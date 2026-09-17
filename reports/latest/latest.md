# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `eaa01fe4fba4a51aa93ca3a4f815e6042216ba5a` · **Modo:** fast

> ⚠️ **Relatório incompleto.** A análise de **architecture** não produziu resultado neste run. O que segue abaixo cobre só 2 das 3 seções esperadas — ausência de finding numa área não avaliada não significa ausência de problema.

## Seções

| Seção | Risco |
|---|---|
| Domínio financeiro | critical |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| FIN-004 | 🔴 critical | finance | 192 | O computed spentRatio do hero do dashboard ainda retorna 0 (em vez de null) quando não há receita no ciclo, e InstrumentReadout.vue renderiza esse 0 como barra 0%-preenchida com 'Dentro da faixa do ciclo' — dado 'sem receita' indistinguível de 'gasto zero real'. |
| FIN-001 | 🟡 medium | finance | 144 | InstrumentReadout continua com o rótulo de razão ('% da renda') hardcoded no componente, então orcamento.vue exibe a leitura textual errada para uma métrica que na verdade mede % do orçamento alocado, não % da renda. |
| FIN-009 | 🔴 critical | finance | 45 | ReimbursementCoverageCalculator pode reportar coverage_pct acima de 100% quando o reembolso do mês de referência excede o gasto do mesmo mês, e esse caso de borda de uma proporção financeira segue sem nenhum teste na suíte atual. |
| FIN-007 | 🔴 critical | finance | 42 | PortfolioService#allocation continua reportando 0.0% de alocação para todos os tipos sempre que o custo líquido total da carteira é zero ou negativo (vendas líquidas superando compras), mesmo havendo posições reais, sem nenhum teste cobrindo total_cost negativo. |
| SEC-003 | 🟢 low | security | 24 | klipper-web voltou a acumular uma advisory moderate (devalue, DoS) além da low já conhecida (esbuild); não há evidência no checkout de que devalue seja exercitado no caminho de request do servidor Nitro em produção (nuxt.config.ts tem ssr:false) — a exposição real depende de quando/como o Nuxt invoca essa dependência, o que este agente não conseguiu confirmar a partir do código-fonte. |
| FIN-005 | 🔴 critical | finance | 16 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição que o próprio código documenta como não verificada contra nenhum débito real, e a suíte de specs não cobre esse caso — dado de patrimônio de import bancário sem cobertura de caso normal (débito). |
| FIN-008 | 🟡 medium | finance | 16 | Uma transação importada via CSV/PDF continua sem nenhuma referência persistida ao arquivo/lote de origem, então não é possível rastreá-la de volta ao extrato que a gerou em nenhuma tela após o import concluir. |
| SEC-006 | 🟢 low | security | 8 | O access token JWT segue em cookie legível por JavaScript (mitigado por CSP com nonce, sem sink de XSS explorável encontrado nesta auditoria), e o ADR-2026-09-17-003 que formalizaria essa aceitação de risco continua com status `proposed`, não decidido. |
| SEC-005 | 🟢 low | security | 6 | O endpoint de redenção do token de reset de senha (PATCH /api/v1/password_resets/:token) continua sem qualquer rate limiting, diferente de todas as outras actions de autenticação não-autenticadas. |
