# Spec 01 — Dinheiro, arredondamento, moeda e datas

**Onde mora:** `app/lib/money.rb` (módulo puro, sem banco) e `app/lib/business_calendar.rb`. Todo calculator e
service usa esses dois; nenhum arredonda por conta própria.

## Regras

1. **D-1.** Dinheiro no banco é `decimal(15,2)` (já é assim). Não migrar para inteiro: o tipo atual já é exato, e a
   migração não corrige nenhum bug. `net_worth_snapshots` passa de `(14,2)` para `(15,2)` para ficar igual às outras.
2. **D-2.** No Ruby, dinheiro é sempre `BigDecimal`. `to_f` só na serialização final, e só enquanto o contrato JSON
   for número (ver D-6).
3. **D-3.** **Uma política de arredondamento:** meio-par (`ROUND_HALF_EVEN`, o "arredondamento bancário" da
   ABNT NBR 5891) a 2 casas, aplicado **só no fim** de cada cálculo, nunca em resultado intermediário.
4. **D-4.** **Divisão de um valor em N partes** (parcela, split por percentual, rateio) não usa arredondamento: usa
   divisão inteira em centavos e entrega o resto a uma parte definida. Soma das partes = total, sempre.
   - Parcelas: o resto vai para a **primeira** parcela (prática do varejo brasileiro).
   - Split por percentual: o resto vai para a **última** parte (assim o usuário vê o "ajuste" no fim da lista).
5. **D-5.** Percentuais de exibição (`pct_used`, `% da renda`) são apresentação: arredondados a 1 casa, nunca
   reentram em conta.
6. **D-6.** O front **não soma dinheiro**. Totais vêm prontos do backend. Onde o front precisar somar (lançamento
   rápido, Fatia 2 de UX), converte para centavos inteiros antes (`Math.round(valor * 100)`) e volta só para exibir.
7. **D-7.** `amount` continua sempre positivo; o sinal é dado pelo tipo e pela conta (ver spec 03).

### Fórmula de divisão em partes

```
total_c = total × 100                         (centavos, inteiro)
base    = ⌊total_c / n⌋
resto   = total_c − base × n                  (0 ≤ resto < n)
parte_k = base + (resto se k é a parte que recebe o resto, senão 0)
```

Exemplo: R$ 1.000,00 em 7 parcelas → `total_c = 100000`, `base = 14285`, `resto = 5` →
**R$ 142,90** + 6 × **R$ 142,85**. Soma: 142,90 + 857,10 = 1.000,00.

## Moeda e câmbio (importante, não essencial)

8. **D-8.** Cada conta tem uma moeda (já existe a coluna). Lançamento herda a moeda da conta.
9. **D-9.** Totais consolidados (patrimônio, painel) são em BRL. Lançamento em moeda estrangeira guarda
   `original_amount`, `original_currency` e `fx_rate`, e `amount` já em BRL. **A taxa fica travada** na data do
   lançamento; recalcular o passado com cotação nova muda número fechado.
9a. **D-9a.** **Representação em moedas diferentes.** `amount` está **sempre na moeda da conta** do lançamento. Para
    conta em BRL com compra em moeda estrangeira: `original_amount` (`decimal(15,2)`, ou casas da moeda),
    `original_currency` (ISO 4217), `fx_rate` (`decimal(18,8)`, BRL por unidade da moeda original) e `fx_rate_on`
    (data da taxa). Invariante: `|amount − original_amount × fx_rate| ≤ 0,005`. Conta em USD guarda `amount` em USD
    e não tem `fx_rate`; a conversão para BRL só acontece em consulta consolidada (D-11), com a taxa e a data
    devolvidas junto do total. Valores de moedas diferentes nunca são somados ou comparados sem conversão explícita.
10. **D-10.** Fonte da cotação: **PTAX de venda** do Banco Central (API Olinda, `CotacaoDolarDia` /
    `CotacaoMoedaDia`), do dia útil anterior quando o dia não tem boletim. Na fatura de cartão a taxa é a que o banco
    aplicou, não a PTAX: quando vier da fatura, prevalece a da fatura.
11. **D-11.** Saldo de conta em moeda estrangeira (ex.: conta global em USD) entra no patrimônio convertido pela PTAX
    do dia do cálculo, e só ele; os lançamentos dela não são reconvertidos.

## Datas e fuso

12. **D-12.** Fuso único `America/Sao_Paulo` (já configurado). "Hoje" é `Date.current`, nunca `Date.today` (que usa o
    fuso do sistema operacional).
13. **D-13.** Lançamento é **data sem horário** (`date`, já é). Não guardar horário.
14. **D-14.** **Competência × caixa.**
    - Conta corrente: competência = caixa = `occurred_on`.
    - Cartão: `occurred_on` = data da compra (registro). Competência = **mês do vencimento da fatura**; caixa = data
      do vencimento (spec 04, K-15a).
    - Relatórios de gasto (orçamento, painel, natureza) usam **competência**. Fluxo de caixa projetado usa **caixa**.
15. **D-15.** O front nunca cria `Date` a partir de string `AAAA-MM-DD` sem meio-dia (`parseISODate`, já existe).
16. **D-16.** Jobs agendados declaram o fuso (`TZ` do processo = `America/Sao_Paulo` ou a expressão de cron com fuso).
    Corrige o R13.

## Calendário de dias úteis

17. **D-17.** `BusinessCalendar.business_day?(data)` = não é sábado, domingo nem feriado bancário nacional.
18. **D-18.** Feriados nacionais fixos: 1/1, 21/4, 1/5, 7/9, 12/10, 2/11, 15/11, 20/11 (Lei 14.759/2023), 25/12.
    Móveis, a partir da Páscoa: Carnaval (segunda e terça, sem expediente bancário), Sexta-feira Santa, Corpus
    Christi. A Páscoa é calculada (algoritmo de Meeus/Jones/Butcher, domínio público), sem tabela por ano.
19. **D-19.** Feriados estaduais e municipais ficam de fora (o banco do Roberto pode ter, mas o erro é de um dia e o
    app avisa "vence em", não paga).

## Casos de borda

| Caso | Regra |
|---|---|
| `0,1 + 0,2` somado no front | Não acontece: o front recebe o total (D-6) |
| R$ 0,01 em 3 parcelas | Resto 1 → 0,01 + 0,00 + 0,00. **Recusar**: parcela de valor zero não é válida; mínimo de 1 centavo por parcela (`total_c ≥ n`) |
| Cálculo com taxa: 1.234,56 × 1,99 % = 24,567744 | Arredonda só no fim → **24,57** |
| Exatamente meio centavo: 2,345 / 2,355 | Meio-par → **2,34** / **2,36** (meio-cima daria 2,35 / 2,36) |
| Compra em USD sem PTAX do dia (sábado) | PTAX do dia útil anterior |
| Feriado de 20/11 antes de 2024 | Não era nacional; a regra vale de 2024 em diante |

## Casos de teste (RSpec)

```ruby
# spec/lib/money_spec.rb
Money.split(BigDecimal("100.00"), 3, remainder: :first)   # => [33.34, 33.33, 33.33]
Money.split(BigDecimal("1000.00"), 7, remainder: :first)  # => [142.90, 142.85 × 6]
Money.split(BigDecimal("100.00"), 3, remainder: :last)    # => [33.33, 33.33, 33.34]
Money.split(BigDecimal("0.01"), 3)                         # => raise ArgumentError
Money.split(x, n).sum == x                                 # propriedade: 200 valores aleatórios × n ∈ 1..48
Money.round(BigDecimal("2.345"))                           # => 2.34
Money.round(BigDecimal("2.355"))                           # => 2.36
Money.round(BigDecimal("1234.56") * BigDecimal("0.0199"))  # => 24.57

# spec/lib/business_calendar_spec.rb
BusinessCalendar.easter(2026)                    # => 2026-04-05
BusinessCalendar.business_day?(Date.new(2026,4,3))  # => false (Sexta-feira Santa)
BusinessCalendar.business_day?(Date.new(2026,2,17)) # => false (terça de Carnaval)
BusinessCalendar.business_day?(Date.new(2026,11,20))# => false
BusinessCalendar.business_day?(Date.new(2023,11,20))# => true
BusinessCalendar.next_business_day(Date.new(2026,11,14)) # sábado → 2026-11-16 (segunda)
BusinessCalendar.next_business_day(Date.new(2026,12,25)) # sexta, Natal → 2026-12-28
```

Fontes públicas: ABNT NBR 5891 (regras de arredondamento); Lei 662/1949 e Lei 14.759/2023 (feriados nacionais);
Banco Central, API de dados abertos Olinda (PTAX).
