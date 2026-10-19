# Spec 13 — Cenários de renda PJ

**Status:** rascunho de 2026-10-19, aguarda aprovação. **Origem:** backlog de 18/10, lacuna 4 (P2).
**Sprint:** depois do D9. **Onde mora:** `PjIncomeScenario` (service puro, usa `Money`); sem tabela nova até o
usuário salvar um cenário.

**Aviso de escopo:** é simulação de planejamento, não apuração fiscal. A tela diz isso. As tabelas legais mudam por
ano; elas ficam em dados versionados (`config/tax_tables/<ano>.yml`), nunca em constante no código.

## Regras

1. **J-1.** Entradas: valor da nota (mensal), pró-labore em % da nota (28 % para o Fator R), custos fixos da PJ,
   receita dos últimos 12 meses (RBT12).
2. **J-2.** **DAS (Simples, Anexo III):** alíquota efetiva pela faixa do RBT12, sobre a nota. A tabela vigente vem do
   arquivo de dados do ano. **A confirmar com o contador** antes da implementação: os números do backlog (R$ 1.236
   sobre R$ 18.000) servem de caso de teste, não de tabela.
3. **J-3.** **INSS do pró-labore:** 11 % sobre o pró-labore, respeitado o teto do ano (no arquivo de dados).
4. **J-4.** **IR do pró-labore:** tabela progressiva do ano com o redutor de 2026, tudo no arquivo de dados.
5. **J-5.** Líquido = nota − DAS − INSS − IR − custos fixos da PJ. Meio-par a 2 casas só no fim (D-3).
6. **J-6.** Comparação lado a lado de **até três** notas. Nada é gravado até o usuário salvar o cenário.
7. **J-7.** O saldo mensal do cenário = líquido − custo mensal do Klipper (spec 12, M-2), com sinal explícito.

## Casos de teste (nota de R$ 18.000)

```ruby
# spec/services/pj_income_scenario_spec.rb   (tabelas de 2026 em fixture de dados)
# pró-labore 28 % = 5.040,00; INSS 11 % = 554,40
# DAS 1.236,00; IR do pró-labore 14,00; custos fixos 280,00
# líquido = 18.000 − 1.236 − 554,40 − 14 − 280 = 15.915,60   (o backlog arredondou para 15.915)
# saldo mensal do backlog: nota 18.000 → −971; nota 20.000 → +529. NÃO reproduzível com o custo mensal de
#   R$ 17.886,41 da spec 12 (15.915,60 − 17.886,41 = −1.970,81). O custo usado no backlog é outro; a premissa
#   precisa ser confirmada pelo Roberto antes de virar teste.
# três notas comparadas → três colunas, 0 registros novos no banco
```

**Pergunta aberta:** de onde vêm as tabelas de DAS e IR de 2026 (contador ou fonte oficial). Sem isso o sprint não abre.
