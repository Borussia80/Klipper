# Spec 11 — Renda fixa com custo de resgate

**Status:** rascunho de 2026-10-19, aguarda aprovação. **Origem:** backlog de 18/10, lacuna 2 (P1).
**Sprint:** abre junto com o D9. **Estende:** spec 02 (C-15, valor de posição) e o modelo de investimento.
**Onde mora:** `FixedIncomePosition` (modelo), `RedemptionCostCalculator` (service, puro, usa `Money`).

O modelo de investimento é de ações (quantidade e preço médio). Faltam os dados que decidem um resgate.

## Regras

1. **F-1.** Cada aplicação de renda fixa guarda: emissor, indexador (`cdi`, `ipca`, `prefixado`), taxa (ex.: 100 %
   do CDI), data de aplicação, vencimento (opcional) e liquidez (`diaria` ou `no_vencimento`).
2. **F-2.** **IR regressivo** sobre o **rendimento** (não sobre o principal), pelo prazo desde a aplicação:
   22,5 % até 180 dias, 20 % de 181 a 360, 17,5 % de 361 a 720, 15 % acima de 720.
3. **F-3.** **IOF regressivo** nos primeiros 29 dias: incide sobre o rendimento, some a partir do dia 30. A tabela
   diária é a do decreto do IOF e **deve ser conferida na implementação**; esta spec não a copia de memória.
4. **F-4.** Custo de resgate = IR + IOF. Cada aporte tem a **sua** data; o custo total é a soma por aporte, não uma
   alíquota única (por isso o IR do Cofrinho dá uma faixa conforme a data de cada aporte).
5. **F-5.** Valor líquido de resgate = valor atual − custo de resgate. É esse valor, e não o bruto, que a reserva em
   meses usa (spec 12).
6. **F-6.** **FGC:** soma por instituição emissora e por CPF; alerta acima de R$ 250.000. Instituição sem dado fica
   "FGC não verificado", nunca "protegido".
7. **F-7.** O rendimento atual vem do valor informado pelo usuário (`position_valuations`, D9); sem valor, o app mostra
   "sem valor atual" e não estima.
8. **F-8.** A tela deixa explícito que é **estimativa de custo**, não extrato; a fonte oficial é a instituição.

## Casos de teste

```ruby
# spec/services/redemption_cost_calculator_spec.rb
# Cofrinhos do Itaú, rendimento 3.682,17: com todos os aportes > 360 dias → 17,5 % = 644,38
#   com todos ≤ 180 dias → 22,5 % = 828,49; mistura de aportes → valor entre os dois
# RDB com aplicação em 01/10: IOF > 0 até 30/10 e "sem IOF" a partir de 31/10
# rendimento zero ou negativo → custo 0 (nunca crédito)
# spec/services/fgc_exposure_spec.rb
# 260.000 numa instituição, um CPF → alerta; 240.000 → sem alerta
```
