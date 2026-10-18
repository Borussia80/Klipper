# 05 — Plano de implementação do domínio

Regras de sempre:
- **Spec antes do código.** Código sem teste não entra.
- Um PR por item, com merge um por vez, esperando o CI do `main`.
- Uso local primeiro, com Postgres de teste via `podman start klipper-pg-test`.
- Toda migração de dados tem rake com `DRY_RUN=1` e relatório antes/depois. O padrão é o backfill do FIN-002.

## Relação com o plano de UX

| Fatia de UX | Depende de |
|---|---|
| 1 Categorias em dois níveis | — (liberada) |
| 2 Lançamento rápido | — (liberada) |
| 3 Painel com patrimônio + vencimento | D2 (saldo) e D4 (ciclo do cartão) |
| 4 Transações e contas | D1 (`kind`), D2 (saldo e histórico) |
| 5 Orçamento | D1 (`countable`), Fatia 1 |
| 6 Agendados | D6 (esta análise substitui a spec 06 de UX quanto às regras) |
| 7 OFX + regras | D5 e D7 |

## Este plano é a referência da implementação

Decisão do Roberto (2026-10-17): a ordem, o escopo e as regras de implementação são **as deste plano e das specs em
`03-specs/`**. Os documentos do Codex são entrada, não plano:

- `docs/specs/klipper_financial_cleanroom_spec_v1.md`: cada requisito e caso está mapeado abaixo para uma sprint e
  uma regra daqui. O que ela pede e este plano não tinha foi incorporado (C-10a/b, L-22/23, I-8a, I-14).
- `docs/reports/*` (locais, fora do Git): servem de consulta para quem planeja, **não** para quem implementa.
- Ordem: o relatório do Codex começa pela importação; este plano começa por D1, porque o pagamento de fatura contado
  como receita (R1) distorce os números de hoje e nenhum dos relatórios o identificou.

**Quem implementa.** Sprints com regra derivada da pesquisa do Sure (D2 saldo e patrimônio, D3 transferência e
split) são implementadas por um agente que **nunca leu** `docs/reports/`, recebendo só a spec clean-room, as specs
deste diretório e o código do Klipper. O agente desta sessão (exposto ao relatório forense, ver `06-registro-pi.md`)
pode implementar D0, D1, D4–D8 e revisar D2/D3 contra os critérios de aceitação, sem escrever o código delas.

| Spec clean-room v1 | Onde está aqui | Sprint |
|---|---|---|
| Req. 1 conta com usuário, moeda, ativo/passivo, abertura | spec 02, C-1, C-2, C-4 | D2 |
| Req. 2 lançamento com conta, data, valor exato, moeda, direção, origem | spec 01, D-1/D-2; spec 03, L-1; spec 06, I-1 | D1, D5 |
| Req. 3 saldo explicável, cache não é história | spec 02, C-3, C-6, C-16 | D2 |
| Req. 4 correção datada e rastreável | spec 02, C-8, C-10a, C-10b | D2 |
| Req. 5 transferência em duas pernas, fora de receita/despesa | spec 03, L-5, L-7, L-8 | D1, D3 |
| Req. 6 reversão em vez de exclusão | spec 03, L-22 | D3 |
| Req. 7 split atômico com soma exata | spec 03, L-20, L-21 | D3 |
| Req. 8 patrimônio datado | spec 02, C-14, C-15; D9 (valor de posição) | D2, D9 |
| Req. 9 importação idempotente por conta e fonte | spec 06, I-1, I-2, I-8a | D5 |
| Req. 10 escopo por usuário | todas as specs; request spec de isolamento em cada endpoint novo | todas |
| Caso 1–2 abertura 1.000, débito 120, retroativo 30 → 850 | spec 02, casos de teste do `AccountBalanceCalculator` | D2 |
| Caso 3 transferência não muda o resultado mensal | spec 03, shared example "ignora transferências" | D1 |
| Caso 4 split 60 + 40 conta uma vez | spec 03, L-20 | D3 |
| Caso 5 correção para 870 auditável | spec 02, C-8, C-10b | D2 |
| Caso 6 duas compras de 50 no mesmo dia | spec 06, I-1 (ordinal) | D5 |
| Caso 7 reimportação idempotente | spec 06, I-2, I-8a | D5 |
| Caso 8 moeda estrangeira com taxa e data | spec 01, D-9 a D-11 | D9 |

## Sprints

### D0 — Fundamentos (1 PR)
- `Money` (`split`, `round` meio-par) e `BusinessCalendar` (Páscoa, feriados nacionais), puros, com specs da spec 01.
- `TZ=America/Sao_Paulo` nos jobs (R13).
- Sem migration.

### D1 — O que conta como receita e despesa (corrige R1 e R6) · **prioridade máxima**
1. M1 (`kind`, `status`) e o scope `Transaction.countable`, com o shared example "ignora transferências" em cada um
   dos 6 calculators.
2. `AutoCategorizerService` sem `/pagamento/` → Renda. Adapters Nubank/Itaú marcam `card_payment`.
3. M2: rake de reclassificação dos pagamentos existentes, `DRY_RUN=1` primeiro, com o relatório de receita por mês
   antes/depois **para o Roberto aprovar**.
4. Front: o painel passa a ler entradas/saídas de `/reports/monthly` (fim da soma no front, R10/R14).

### D2 — Saldo derivado e reconciliação (corrige R4 e R5)
- M5, `AccountBalanceCalculator`, `ReconciliationService`, M7, `NetWorthCalculator` com ativo/passivo e conta
  arquivada.
- Tipos `cash`, `receivable`, `loan`.
- `GET /accounts/:id/balance_history` (Fatia 4 de UX).

### D3 — Transferência e estorno
- M6, `TransferService`, `RefundService`, detecção na importação (spec 03, L-12) e ferramenta "ligar pares".

### D4 — Cartão
- M8, `CardCycle`, `CardStatementCalculator` (total, status, limite, rotativo), M9, `InstallmentPlanService`
  (parcelas previstas).
- Libera a validação de data futura para `previsto` (R7).
- `DebtRankingCalculator` passa a ler `financiado` da fatura.

### D5 — Importação (corrige R2, R3 e R11)
- M3, M4, `ImportMatcher` (porte do Actual), pré-visualização para CSV, mapeamento de colunas, desfazer.
- M10 no fim do sprint.

### D6 — Recorrências
- M11, `RecurrenceRule`, `ScheduledOccurrencesCalculator` (portes P2/P3 do ezBookkeeping), conciliação sugerida.

### D7 — Regras e aprendizado
- M12, `RuleEngine` (desenho do Actual), aprendizado, tela de regras.

### D8 — Orçamento
- `countable` no `BudgetEngine` (já feito em D1), `rollover`, alertas 80 %/100 % e ritmo.

### D9 — Planejamento e investimentos (importante, depois do essencial)

Fórmulas registradas para quando o sprint for aberto:

- **Rentabilidade da carteira: recomendação TWR mensal por Dietz modificado.** Neutraliza o efeito dos aportes, o
  que permite comparar com o CDI. A TIR (MWR) responde outra pergunta ("quanto *eu* ganhei com meu timing") e fica
  como segunda leitura.
  `r = (V₁ − V₀ − F) / (V₀ + Σ wᵢ·Fᵢ)`, com `wᵢ = (dias do mês − dia do aporte) / dias do mês`.
  Exemplo: V₀ 10.000, aporte de 2.000 no dia 15 de um mês de 30, V₁ 12.300 → **2,73 %**. Encadeamento:
  `TWR = Π(1 + rₘ) − 1`.
- **CDI:** série SGS 12 (CDI diário, % a.d.) do Banco Central. Acumulado = `Π(1 + dᵢ) − 1` nos dias úteis do período.
  `% do CDI = r_carteira / r_CDI`. Exemplo: CDI de 11,04 % a.a. → 0,0393 % a.d. → 0,8279 % em 21 dias úteis; a
  carteira rendeu 0,95 % → **114,75 % do CDI**.
- **Real (IPCA):** série SGS 433 (IPCA mensal). `real = (1 + nominal) / (1 + IPCA) − 1`. Exemplo: 12 % nominal e
  4,5 % de IPCA → **7,18 %** (e não 7,5 %).
- **Valor de posição:** atualização manual (`position_valuations`: posição, data, valor) e, para ações, a cotação que
  o `StockQuoteService` já busca. Patrimônio passa a usar o valor quando houver e o custo quando não houver (spec 02,
  C-15).
- **Meta de economia:** aporte mensal `PMT = FV · i / ((1 + i)ⁿ − 1)`. R$ 12.000 em 12 meses a 0,8 % a.m. →
  **R$ 956,76/mês**.
- **Fluxo de caixa projetado:** `saldo_previsto` (spec 02, C-5) dia a dia, por data de **caixa** (spec 01, D-14:
  cartão pelo vencimento), somando previstos de agendados, parcelas e faturas.
- **Quitação de dívida:** avalanche (maior taxa primeiro, o ranking atual) × bola de neve (menor saldo primeiro), com
  a mesma fórmula de juros do rotativo.

## Itens a portar

| # | Origem (licença, commit) | O que faz | Destino no Klipper | Sprint |
|---|---|---|---|---|
| A1 | Actual `packages/loot-core/src/server/accounts/sync.ts` → `matchTransactions`, `compareFuzzyMatchCandidates` (MIT, `bde50c3`) | Três passadas de casamento na importação, com casamento único | `app/services/import_matcher.rb` | D5 |
| A2 | Actual `server/rules/rule-utils.ts` → `computeScore`, `rankRules` (MIT, `bde50c3`) | Ordem determinística das regras por especificidade | `app/services/rule_engine.rb` | D7 |
| A3 | Actual `server/transactions/transaction-rules.ts` → `getProbableCategory`, `updateCategoryRules` (MIT, `bde50c3`) | Aprendizado: 5 recentes, 3 votos | `app/services/category_learning.rb` | D7 |
| A4 | Actual `shared/rules.ts` → `getApproxNumberThreshold` (MIT, `bde50c3`) | Limiar de 7,5 % do "aproximadamente" | `RuleEngine` / `ImportMatcher` | D5 |
| P2/P3 | ezBookkeeping, já listados no plano de UX (MIT, `ff168cf`) | Agendados e ocorrências | D6 | D6 |
| P6 | ezBookkeeping `pkg/converters/ofx/` (MIT, `ff168cf`) | Leitor de OFX | `app/services/bank_import/ofx_reader.rb` | D5 |

O porte é para Ruby: a lógica é reescrita, não colada. Mesmo assim, o arquivo leva o cabeçalho de atribuição e
entra no `THIRD_PARTY_NOTICES.md`. A licença do Actual é "Copyright James Long", MIT.

Do Actual **não** se porta o desenho de envelope (spec 08) nem o `transfer.ts` (a regra de "limpar categoria
quando as duas contas estão no orçamento" é conceito, já reescrito na spec 03 com palavras próprias).

## Riscos do plano

| Risco | Mitigação |
|---|---|
| A reclassificação M2 erra e some receita verdadeira (ex.: "Pagamento de salário") | `DRY_RUN` com lista linha a linha; só linhas de **conta cartão**; aprovação do Roberto antes de rodar |
| Saldo derivado ≠ saldo real porque o histórico importado começa no meio | Saldo inicial na data do primeiro lançamento + primeira reconciliação |
| Ciclo de fatura do banco ≠ regra K-5 | Fatura do PDF manda; mover compra entre faturas |
| Calculator esquecido sem `countable` | Shared example obrigatório + grep no CI por `transactions.where(transaction_type:` fora do scope |
| Sprint D1 muda os números do painel | Esperado. O PR mostra antes/depois com os dados locais |

## Decisões que dependem do Roberto

| # | Decisão | Recomendação |
|---|---|---|
| Q1 | Modelo simples com pares × partidas dobradas | **Simples com pares** (`04-modelo-dados.md`) |
| Q2 | Orçamento limite × envelope | **Limite**, com rollover opcional |
| Q3 | Parcela conta no mês da fatura × da compra | **Da fatura** (K-15) |
| Q4 | Compra no dia do fechamento vai para a próxima fatura (K-5)? Conferir no Nubank e no Itaú | Sim, até conferir |
| Q5 | Estouro do orçamento reduz o mês seguinte? | **Não** |
| Q6 | Rodar a reclassificação dos pagamentos de fatura (M2) | Sim, depois do `DRY_RUN` |
| Q7 | Saldo inicial: digitar por conta ou conciliar uma vez | **Conciliar uma vez** |
| Q8 | Rentabilidade: TWR (Dietz) principal, TIR secundária | **TWR** |
| Q9 | URLs da interface do Sure e do ezBookkeeping para a sessão de observação (os `[URL_…]` do pedido vieram vazios) | Opcional: as specs não dependem delas |
