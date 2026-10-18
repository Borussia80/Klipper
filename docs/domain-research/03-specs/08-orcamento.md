# Spec 08 — Orçamento: limite × envelope, estouro, rollover

**Onde mora:** `BudgetEngine` (já existe). Passa a usar `Transaction.countable` e a regra pai × filha já especificada
na Fatia 1 de UX (`docs/ux-research/05-specs/07-categorias.md`).

## Decisão: modo limite, não envelope

| | Envelope (YNAB, Actual) | Limite (teto de gasto) |
|---|---|---|
| Pergunta | "Para onde vai cada real que já tenho?" | "Quanto posso gastar nesta categoria?" |
| Exige | Saldo real de todas as contas, todo mês, e alocar 100 % da renda | Só lançamentos |
| No Klipper hoje | Impossível: saldo não existe (R4) | É o que existe |
| Disciplina | Alta, diária | Baixa, mensal |

**Recomendação: manter o modo limite.** O envelope depende do saldo derivado (spec 02) e de um hábito de alocação
mensal que o app não tem hoje. Pode virar opção depois que saldo e conciliação estiverem de pé, mas não muda o
modelo: envelope é limite + rollover obrigatório + "a alocar".

## Regras

1. **O-1.** `gasto(categoria, mês)` = Σ `debit countable` − Σ `refund` da categoria (e das filhas, Fatia 1) no mês,
   por **mês de contabilização** (spec 01, D-14; cartão pelo vencimento da fatura, spec 04, K-15a).
2. **O-2.** `restante = limite − gasto`; `pct = gasto / limite` (só exibição). Sem limite → `null`, não 0 % (o bug do
   `InstrumentReadout.vue:28,62` faz `spentRatio ?? 0` sobre o `null` que `orcamento.vue:118` recebe; já registrado).
3. **O-3.** Gasto negativo (estorno maior que o gasto no mês) aparece como crédito, não como 0 %.
4. **O-4.** **Rollover opcional por orçamento** (`rollover: boolean`, padrão `false`):
   `limite_efetivo(m) = limite(m) + max(restante(m − 1), 0)` se `rollover`. Só sobra positiva passa; estouro **não**
   reduz o mês seguinte (decisão de produto: punir o mês seguinte faz o usuário abandonar o orçamento).
5. **O-5.** Alertas: 80 % ("ação em breve") e 100 % ("ação agora"), com as prioridades de alerta do `tokens.css`. O ritmo
   do mês (Fatia 5 de UX) entra junto: gasto acima de `limite × dia / dias_no_mês` + 10 % → "acima do ritmo".
6. **O-6.** Copiar o mês anterior (`POST /budgets/copy_previous`, já planejado) copia limites e `rollover`, não
   sobras.

## Exemplo

Mercado, limite R$ 1.000,00 com rollover. Setembro: gasto 850 → sobra 150. Outubro: limite efetivo **1.150**; gasto
1.200 com estorno de 80 → gasto **1.120**, restante **30**, 97,4 % → alerta "ação em breve".

## Casos de teste (RSpec)

```ruby
# spec/services/budget_engine_spec.rb (acréscimos)
# transferência e pagamento de fatura na categoria não entram no gasto
# estorno de 80 abate: 1200 − 80 = 1120
# parcela 3/7 de 142,85 entra no mês da fatura, não no da compra
# rollover: setembro sobra 150 → outubro limite efetivo 1150; setembro estoura 200 → outubro 1000
# sem rollover → limite efetivo = limite
# previsto não entra no gasto
```
