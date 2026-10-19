# Spec 12 — Reserva em meses e projeção com atrasos de recebimento

**Status:** rascunho de 2026-10-19, aguarda aprovação. **Origem:** backlog de 18/10, lacuna 3 (P1).
**Sprint:** abre junto com o D9. **Estende:** spec 02 (`saldo_previsto`, C-5), spec 01 (D-14, competência × caixa) e
a spec 11 (custo de resgate).
**Onde mora:** `EmergencyReserveCalculator` e `CashflowProjector` (services puros).

A projeção do fim do mês corrente não basta: a decisão de outubro precisou de seis meses à frente, com receitas que
chegam atrasadas.

## Regras

1. **M-1.** **Reserva em meses** = (saldo das contas líquidas + investimentos líquidos do custo de resgate, spec 11)
   ÷ custo mensal. Resultado com 2 casas, meio-par, só no fim (D-3).
2. **M-2.** **Custo mensal** = média de despesa `countable` dos últimos N meses fechados (N configurável, padrão 3),
   sem transferência nem pagamento de fatura (D1). A tela mostra N e o valor usado.
3. **M-3.** **Meta** em meses é configurável. A linha da meta aparece no gráfico: meta × custo mensal (6 meses ×
   R$ 17.886,41 = R$ 107.318,46).
4. **M-4.** **Receita prevista com defasagem por fonte:** cada fonte de renda tem `atraso_dias` (a nota PJ cai de 30 a 45
   dias depois do mês trabalhado; reembolso do plano, um mês depois). A projeção usa a data de **caixa** (D-14).
5. **M-5.** Rendimento da reserva entra como receita **variável**; nunca reduz despesa.
6. **M-6.** A tela lista **o que entrou** na projeção e **o que ficou de fora** (sem data, sem valor, sem fonte).
   Item sem data nunca é chutado.
7. **M-7.** Horizonte padrão de 6 meses; cada mês mostra saldo projetado e cobertura em meses. Cenário é um
   parâmetro de leitura, não grava nada (ver spec 13).

## Casos de teste

```ruby
# spec/services/emergency_reserve_calculator_spec.rb
# 130020.78 / 17886.41 → 7.27 meses
# meta 6 meses com custo 17886.41 → 107318.46
# investimento com custo de resgate: usa o líquido, não o bruto
# sem N meses de histórico → usa os que existem e sinaliza "histórico curto"
# spec/services/cashflow_projector_spec.rb
# nota prevista em 05/11 com atraso 30–45 dias → entra em 05/12 (início do intervalo) e a tela mostra o intervalo
# lançamento previsto sem data → listado em "ficou de fora"
# rendimento da reserva → linha de receita variável
```

**A decidir:** o ponto do intervalo de atraso usado no cálculo (início, meio ou fim). Proposta: **fim do intervalo**
(o mais conservador para a reserva). Aguarda o Roberto.
