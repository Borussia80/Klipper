# Spec 04 — Cartão de crédito: fatura, parcelas, limite, pagamento, rotativo, IOF, estorno

**Onde mora:**
- `CardCycle`: puro (`app/lib`), calcula datas de fechamento e vencimento.
- `CardStatement`: model; a fatura é materializada.
- `InstallmentPlanService`: transacional, gera e cancela as parcelas.
- `CardStatementCalculator`: consulta (total, pago, status, limite).

Substitui os campos digitados `saldo_fatura_atual` e `pagamento_minimo` como fonte da verdade. `juros_rotativo_am`
continua digitado, porque é dado do contrato.

## Ciclo da fatura

1. **K-1.** Conta cartão ganha `dia_fechamento` e `dia_vencimento` (1–31) e `limite` (`decimal(15,2)`), como já
   registrado na Fatia 3 de UX.
2. **K-2.** **Dia que o mês não tem** → último dia do mês (31 em abril = 30/04; 31 em fevereiro = 28/02 ou 29/02 em
   ano bissexto).
3. **K-3.** **Fechamento não se desloca** por fim de semana ou feriado. O banco fecha no dia mesmo sem expediente.
4. **K-4.** **Vencimento em dia não útil** → próximo dia útil (`BusinessCalendar`, spec 01). É a regra da Resolução
   CMN 4.549 / prática de mercado: pagamento no dia útil seguinte sem encargo.
5. **K-5.** **A que fatura pertence uma compra:** compra com `data < fechamento do mês` entra na fatura que fecha
   neste mês; `data ≥ fechamento` entra na seguinte. **O dia do fechamento é o "melhor dia de compra"**: a compra dele
   só é paga no vencimento do mês seguinte. *(Os bancos diferem neste ponto; ver decisão D4 em `05-plano`.)*
6. **K-6.** Vencimento da fatura que fecha no mês M = `dia_vencimento` em M se `dia_vencimento > dia_fechamento`,
   senão em M+1. Depois aplica K-2 e K-4.
7. **K-7.** A fatura é uma linha em `card_statements` (`account_id`, `closing_on`, `due_on`) criada sob demanda. A
   compra recebe `card_statement_id`. O usuário pode **mover** uma compra para outra fatura (o corte real do banco às
   vezes diverge), e a fatura importada do PDF manda: as linhas do PDF ficam na fatura do PDF.

### Exemplo resolvido (fechamento 3, vencimento 10)

| Compra | Fatura (fecha) | Vence | Observação |
|---|---|---|---|
| 02/10/2026 | 03/10/2026 | **13/10/2026** | 10/10 é sábado, 12/10 é feriado (N. Sra. Aparecida) → terça 13/10 |
| 03/10/2026 | 03/11/2026 | 10/11/2026 | Melhor dia de compra: pagamento só em novembro |
| 04/10/2026 | 03/11/2026 | 10/11/2026 | |

Fechamento 31: fatura de fevereiro/2026 fecha em **28/02**, a de fevereiro/2028 em **29/02**, a de abril em **30/04**.

## Total, pagamento e status da fatura

```
total(f)  = Σ debit(f) − Σ credit regular/refund(f)  + saldo_anterior(f) + encargos(f)
pago(f)   = Σ card_payment ligados a f
restante  = total − pago
```

8. **K-8.** Status: `aberta` (hoje < fechamento) · `fechada` (fechou, restante > 0, hoje ≤ vencimento) · `paga`
   (restante ≤ 0) · `em_atraso` (hoje > vencimento e restante > 0).
9. **K-9.** Pagamento é transferência corrente → cartão com `kind: card_payment` (spec 03, L-11) e liga à fatura
   **fechada mais antiga com restante > 0**; se não houver, à aberta (pagamento antecipado).
10. **K-10.** **Pagamento parcial:** `restante` vira `saldo_anterior` da próxima fatura (rotativo). Não se cria
    lançamento novo: o saldo da conta cartão já está certo pelas transferências (spec 02, C-3).
11. **K-11.** **Encargos do rotativo são estimados, não lançados.** A estimativa é para a tela ("se pagar só isso,
    a próxima fatura terá ~R$ X de juros"). O valor real chega na fatura seguinte como linha de "Juros" / "IOF" /
    "Encargos" e entra como despesa comum, na categoria "Encargos financeiros".

```
financiado      = max(restante, 0)
juros_estimado  = financiado × juros_rotativo_am                      (taxa do contrato, digitada)
iof_estimado    = financiado × 0,38 % + financiado × 0,0082 % × dias   (dias até o próximo vencimento, máx. 365)
teto (Lei 14.690/2023) = juros + encargos acumulados de uma dívida de rotativo ≤ 100 % do principal original
```

   Exemplo: fatura de R$ 2.000,00, pagou o mínimo de R$ 300,00, juros de 14 % a.m., 30 dias →
   financiado 1.700,00; juros **238,00**; IOF 6,46 + 4,18 = **10,64**; próxima fatura ≈ 1.700 + 248,64 + compras novas.
   (O `DebtRankingCalculator` atual faz a parte dos juros; passa a ler `financiado` daqui em vez de
   `saldo_fatura_atual − pagamento_minimo`.)

## Limite

```
limite_usado      = −saldo_previsto(cartão, ∞)   (spec 02: inclui faturas não pagas e parcelas previstas futuras)
limite_disponível = limite − limite_usado
```

12. **K-12.** Parcelas futuras ocupam limite desde a compra (é assim que os bancos fazem). Por isso entram como
    `previsto`, e o limite usa o saldo previsto.
13. **K-13.** Disponível negativo é mostrado (estouro), não truncado em zero.

## Compras parceladas

14. **K-14.** Uma compra de `n` parcelas = 1 `installment_plan` (`total`, `n`, `taxa_am`, `first_statement_id`,
    `descrição`) + `n` lançamentos `debit`. Parcela 1 nasce `efetivado` na fatura da compra; parcelas 2..n nascem
    `previsto`, cada uma na fatura seguinte à anterior, com `installment_number`/`total` (já existem).
15. **K-15.** **Competência da parcela = fatura em que ela cai** (não a data da compra). Assim orçamento e natureza
    `cartao_parcelamento` mostram R$ 142,90 por mês, e não R$ 1.000 no mês da compra. É o que a importação de PDF já
    faz hoje (cada fatura traz a sua "03/07").
15a. **K-15a.** **Uma regra só para todo lançamento de cartão** (à vista, parcela, estorno, encargo): o mês de
    competência é o **mês do vencimento da fatura** em que a linha está. Orçamento, natureza, painel e relatórios de
    receita/despesa usam esse mês; o fluxo de caixa usa a **data** do vencimento. Exemplo (fecha 3, vence 10): compra
    à vista em 02/10/2026 → fatura que vence 13/10 → outubro; compra em 03/10/2026 → vence 10/11 → novembro, nos dois
    relatórios. Mover a compra para outra fatura (K-7) muda o mês de competência junto. Depende da decisão Q3.
16. **K-16.** **Sem juros:** valores por `Money.split(total, n, remainder: :first)` (spec 01, D-4).
    R$ 1.000,00 em 7× → 142,90 + 6 × 142,85.
17. **K-17.** **Com juros (Tabela Price):** `PMT = PV · i / (1 − (1 + i)^−n)`, arredondada a 2 casas. O resíduo da
    última parcela fecha o total que o banco informa.
    R$ 1.000,00 a 2 % a.m. em 12× → PMT = 94,5596 → **94,56**; total **1.134,72**. Quando o usuário digitar o valor
    da parcela (caso comum: a loja diz "12× de 94,56"), a taxa não é necessária: grava-se o valor dado.
18. **K-18.** **Importação** de uma linha "LOJA 03/07": procura o plano da mesma conta com descrição semelhante e
    `n = 7`. Se achar, **concilia** com a parcela 3 prevista (vira efetivada, valor do PDF prevalece); se não achar,
    cria o plano a partir dela, com as parcelas 4..7 previstas e as 1..2 não criadas (passado anterior ao app).
19. **K-19.** **Antecipação / quitação antecipada:** o usuário informa quais parcelas e o valor pago. As previstas
    antecipadas são canceladas e um lançamento único com o valor pago entra na fatura aberta. Com juros, o CDC
    (art. 52, §2º) garante a redução proporcional dos juros. A estimativa mostrada é o valor presente:
    `VP = Σ PMT / (1 + i)^k`. No exemplo, antecipar as 4 últimas: 4 × 94,56 = 378,24 → VP **360,06**.

## Compra internacional (importante)

20. **K-20.** Guarda `original_amount` e `original_currency`. `amount` em BRL = original × taxa aplicada pelo banco
    (vem da fatura). Sem a taxa da fatura (lançamento manual), usa PTAX de venda (spec 01, D-10) e marca
    "estimado".
21. **K-21.** IOF é **lançamento separado** (como o banco imprime), categoria "Encargos financeiros". Alíquota numa
    tabela com vigência (`iof_rates`: `desde`, `aliquota`), não fixa no código: mudou em 2022, 2023 e 2025.
    Exemplo com 3,5 %: US$ 100,00 × 5,40 = R$ 540,00; IOF **R$ 18,90**.

## Estorno no cartão

22. **K-22.** Estorno em fatura aberta: crédito na fatura aberta, reduz o total (spec 03, L-16).
23. **K-23.** Estorno que chega depois do fechamento da compra: entra na fatura aberta **quando chega**. Se passar
    do total da fatura, o total fica negativo = **saldo credor**, que abate a fatura seguinte.
24. **K-24.** Estorno de compra parcelada inteira: parcelas previstas canceladas; parcelas já faturadas recebem um
    crédito único na fatura aberta.

## Casos de teste (RSpec)

```ruby
# spec/lib/card_cycle_spec.rb  (fechamento 3, vencimento 10)
CardCycle.statement_for(Date.new(2026,10,2))  # => closing 2026-10-03, due 2026-10-13
CardCycle.statement_for(Date.new(2026,10,3))  # => closing 2026-11-03, due 2026-11-10
# fechamento 31: fevereiro 2026 → 2026-02-28; fevereiro 2028 → 2028-02-29; abril → 2026-04-30
# fechamento 25, vencimento 5 → vence no mês seguinte
# vencimento cai em 01/01 → próximo dia útil
# fechamento num domingo → não muda

# spec/services/installment_plan_service_spec.rb
plan(1000, 7, sem juros) # => parcelas [142.90, 142.85×6], sum == 1000.00, 1 efetivada + 6 previstas em faturas consecutivas
plan(1000, 12, taxa 2%)  # => 12 × 94.56
plan(0.05, 7)            # => erro (parcela < 1 centavo)
# importação "LOJA 03/07" com plano existente → concilia, não cria
# importação "LOJA 03/07" sem plano → cria plano, previstas 4..7
# antecipar 4 últimas com taxa 2% → estimativa 360.06; previstas canceladas; 1 lançamento na aberta
# estorno da compra parcelada após a 2ª fatura → 5 previstas canceladas, crédito de 285.75 na aberta

# spec/services/card_statement_calculator_spec.rb
# total 2000, pago 300, 14% a.m., 30 dias → financiado 1700, juros 238.00, iof 10.64
# pago 2000 → status paga; pago 0 e hoje > vencimento → em_atraso
# limite 5000, saldo -1200, previstas -600 → disponível 3200
# estorno maior que a fatura → total negativo, abate a próxima
```

Fontes públicas: Banco Central, Resolução CMN 4.549/2017 (rotativo); Lei 14.690/2023 (teto de juros do rotativo);
Código de Defesa do Consumidor, art. 52, §2º; Decreto 6.306/2007 e alterações (IOF); fórmula da Tabela Price
(matemática financeira, domínio público).
