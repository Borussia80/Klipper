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

**Quem implementa.** Atualizado em 2026-10-17, depois da investigação de hledger (GPL), Firefly III e Data
Importer (AGPL). O agente desta sessão leu o código desses projetos e o relatório forense do Sure, então fica
**exposto** a quase todo o domínio:

| Sprint | Pesquisa que a toca | Quem escreve o código |
|---|---|---|
| D0 Fundamentos | nenhuma | esta sessão pode |
| D1 O que conta | nenhuma (bug do Klipper) | esta sessão pode |
| D2 Saldo, conferência, patrimônio | Sure, hledger | agente limpo |
| D3 Transferência, split, reversão | Sure, hledger | agente limpo |
| D4 Cartão | nenhuma | esta sessão pode |
| D5 Importação | Actual (MIT), Data Importer, hledger | agente limpo |
| D6 Recorrências | Firefly | agente limpo |
| D7 Regras | Actual (MIT), Firefly | agente limpo |
| D8 Orçamento | Firefly | agente limpo |

"Agente limpo" = sessão nova que **nunca leu** `docs/reports/` nem o código de hledger, Firefly, Data Importer ou
Sure, e recebe só `docs/specs/klipper_financial_cleanroom_spec_v2.md`, as specs deste diretório e o código do
Klipper. Esta sessão revisa o resultado contra os critérios de aceitação, sem escrever o código. Os portes MIT do
Actual e do ezBookkeeping (tabela "Itens a portar") continuam permitidos com atribuição, mas também ficam com o
agente limpo quando caem em D5/D7.

**Spec clean-room v2** (`docs/specs/klipper_financial_cleanroom_spec_v2.md`) substitui a v1 como entrada do
implementador. Regras novas que ela trouxe e que foram incorporadas aqui: G-13 (regras avaliam o estado original),
G-14 (ação com alvo inexistente é rejeitada ao salvar), G-15 (auditoria de cada aplicação), I-6a (estado
`conflito`), I-6b (excluído não volta sem pedido), I-6c (retroativo publicado depois é novo), R-11 (pausar e
retomar; nada depende de o processo rodar no dia).

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

## Política de código de terceiros (2026-10-17)

| Projeto | Licença | Regra |
|---|---|---|
| Sure, hledger, Firefly III, Data Importer | AGPL / GPL | Só pesquisa e especificação funcional. **Nenhum** código, teste, pseudocódigo ou estrutura interna entra no Klipper |
| Actual Budget, ezBookkeeping | MIT | **Padrão: reimplementar** a funcionalidade a partir das specs, sem abrir o código de referência durante a implementação. Reaproveitar código de fato é **exceção**, aprovada pelo Roberto caso a caso, com análise de licença, cabeçalho de atribuição e entrada no `THIRD_PARTY_NOTICES.md` |

Exceção já aprovada: **P1** (`amountExpression`, Fatia 2 de UX, a partir do `evaluator.ts` do ezBookkeeping), no
plano de UX aprovado em 2026-10-17. As demais referências MIT abaixo são funcionalidades a reimplementar, não portes:

| # | Referência (MIT) | Funcionalidade | Onde está a regra | Sprint |
|---|---|---|---|---|
| A1 | Actual, casamento na importação | Três passadas, casamento único, data mais próxima | spec 06, I-4/I-5 | D5 |
| A2 | Actual, ordem das regras | Ordem por especificidade, desempate estável | spec 07, G-4 | D7 |
| A3 | Actual, aprendizado | 5 recentes, 3 votos | spec 07, G-10 a G-12 | D7 |
| A4 | Actual, "aproximadamente" | Limiar de 7,5 % | spec 07, G-2 | D5/D7 |
| P2/P3 | ezBookkeeping, agendados | Agendado e ocorrências | spec 05 | D6 |
| P6 | ezBookkeeping, OFX | Leitor OFX 1.x/2.x | spec 06, I-13 | D5 |

Envelope (Actual) fica fora (spec 08).

## Riscos do plano

| Risco | Mitigação |
|---|---|
| A reclassificação M2 erra e some receita verdadeira (ex.: "Pagamento de salário") | `DRY_RUN` com lista linha a linha; só linhas de **conta cartão**; aprovação do Roberto antes de rodar |
| Saldo derivado ≠ saldo real porque o histórico importado começa no meio | Saldo inicial na data do primeiro lançamento + primeira reconciliação |
| Ciclo de fatura do banco ≠ regra K-5 | Fatura do PDF manda; mover compra entre faturas |
| Calculator esquecido sem `countable` | Shared example obrigatório + grep no CI por `transactions.where(transaction_type:` fora do scope |
| Sprint D1 muda os números do painel | Esperado. O PR mostra antes/depois com os dados locais |

## Decisões Q1–Q11 — versão final (aprovadas pelo Roberto em 2026-10-17)

| # | Decisão | Versão final | Onde está |
|---|---|---|---|
| Q1 | Modelo de dados | **Lançamento simples com pares** (`kind`, `status`, `transfer_pair_id`), sem partidas dobradas | `04-modelo-dados.md` |
| Q2 | Modelo de orçamento | **Limite mensal por categoria**, rollover opcional só de sobra; envelope fora | spec 08 |
| Q3 | Mês dos gastos de cartão | **Mês de contabilização = mês do vencimento da fatura**, derivado e explícito; a data original da compra é preservada e nunca sobrescrita | spec 04, K-15a; spec 01, D-14 |
| Q4 | Compra no dia do fechamento | **Vai para a fatura seguinte** (padrão do sistema). Pendente: o Roberto conferir no Nubank e no Itaú; se um banco divergir, vira opção por conta, sem mudar a regra geral | spec 04, K-5 |
| Q5 | Estouro reduz o mês seguinte | **Não** | spec 08, O-4 |
| Q6 | Reclassificar pagamentos de fatura já gravados (M2) | **Sim**, só depois do `DRY_RUN` e da aprovação do relatório de receita por mês antes/depois | Sprint D1 |
| Q7 | Saldo inicial | **Conferir com o banco uma vez** por conta, em vez de digitar | spec 02, C-10 |
| Q8 | Rentabilidade | **TWR por Dietz modificado**, TIR como segunda leitura | D9 |
| Q9 | Observar a interface do Sure e do ezBookkeeping | **Não necessário**; as specs não dependem disso | — |
| Q10 | CAMT.052/053 | **Não implementar** | spec 06 |
| Q11 | Reaplicar regras ao editar | **Não**; regras só em lançamento novo ou reaplicação explícita | spec 07, G-8 |

Condições da aprovação: deduplicação sem identificador do banco sinaliza ambiguidade em vez de prometer acerto
(spec 06, "Limites"); moeda e conversão conforme spec 01, "Semântica de moeda"; nenhuma fatia 3–6 é antecipada.
