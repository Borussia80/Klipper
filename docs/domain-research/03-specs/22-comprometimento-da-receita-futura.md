# Spec 22 — Comprometimento da receita futura

**Status:** rascunho de 2026-11-19, revisão 2 (ressalvas da revisão de 19/11 incorporadas), aguarda aprovação.
**Domínio:** Debt Management, transversal (ADR-2026-11-19-007).
**Depende de:** spec 04 (K-5, K-12, K-13, K-14, K-15a), spec 05 e 14 (recorrências e encargos), spec 19
(financiamento), spec 12 (M-2, M-6), spec 13 (cenários PJ), spec 21 (provisões), spec 01 (D-3, D-4).
**Onde mora:** `CommitmentCalculator` e `PurchaseSimulator` (services puros, sem gravação).

Mostrar, mês a mês, quanto da receita futura já está tomado e quanto uma nova compra tomaria, antes de ela ser
feita. É o caso da TV parcelada: a pessoa compra contando com a receita do mês seguinte; o Klipper mostra se essa
receita ainda está livre.

## Regras

1. **CR-1.** **Receita de referência** do mês m, sempre líquida, em uma de três fontes, nesta ordem de preferência:
   (a) cenário salvo da spec 13; (b) valor manual informado; (c) padrão conservador = **menor** receita líquida mensal
   efetivada nos últimos 6 meses fechados. Com menos de 3 meses fechados e sem (a) ou (b), o indicador não é
   calculado e a tela pede o valor. A tela sempre mostra a fonte usada.
2. **CR-2.** **Componentes do mês m**, cada item contado uma vez pelo seu identificador:
   - (a) itens de fatura de cartão (parcelas previstas da K-14 e compras já lançadas) cujo mês de contabilização
     (K-15a) é m;
   - (b) prestações de financiamento (spec 19) com vencimento em m;
   - (c) ocorrências de recorrências e encargos de despesa (specs 05 e 14) em m, que não sejam pagamento de fatura,
     **sempre pelo valor integral**;
   - (d) contribuições planejadas de provisão (spec 21, PV-11) em m;
   - (e) cobertura por provisão alocada a ocorrências de (c) em m (spec 21, PV-12). Nunca maior que a ocorrência.
3. **CR-3.** **Indicadores** (só exibição, a partir de centavos, 1 casa, meio-par, D-3):
   - comprometimento com dívidas = (a + b) ÷ receita;
   - comprometimento bruto da renda = (a + b + c) ÷ receita;
   - comprometimento líquido da renda = (a + b + c − e + d) ÷ receita.
   O bruto mostra a obrigação inteira, mesmo já coberta. O líquido mostra o que de fato depende da receita do mês.
   Receita zero → `null`, nunca 0 % ou infinito.
4. **CR-4.** **Sem contagem dupla.**
   - Uma recorrência cobrada no cartão aparece em (a) no mês em que vira item de fatura, e a ocorrência prevista
     correspondente sai de (c).
   - O pagamento de fatura nunca é compromisso. A transferência entre contas próprias nunca é compromisso.
   - Uma ocorrência coberta por provisão continua em (c) pelo valor integral. A cobertura entra só em (e), e a
     constituição da provisão nunca entra em nenhuma camada.
5. **CR-5.** **Margem livre estimada** = receita − (a + b + c − e + d) − gasto variável de referência. Pode ser
   negativa e é mostrada assim. O nome na tela é "margem livre estimada", nunca "disponível".
6. **CR-6.** **Gasto variável de referência, sem dupla contagem.** Para cada categoria k no mês m:
   `variavel(k, m) = max(0, base(k) − compromissos(k, m))`, em que `base(k)` é o limite da spec 08 se houver, senão a
   média de despesa variável dos últimos 3 meses fechados (spec 12, M-2), e `compromissos(k, m)` é a soma de (a) e (c)
   já contada naquela categoria. O total é a soma das categorias.
7. **CR-7.** **Simulação de compra.** Entradas: valor, n parcelas, categoria, cartão e data da compra. Nada é
   gravado. As parcelas são divididas pela D-4 (resto na primeira). O mês da primeira parcela é o mês de
   contabilização da fatura em que a compra cai (K-5, K-15a). Compra no débito ou Pix compromete só o mês corrente.
8. **CR-8.** O resultado da simulação mostra, por mês, os três indicadores antes e depois, a margem livre estimada,
   a faixa de cada indicador e o mês da última parcela. O horizonte vai até o mês seguinte à última parcela, com
   mínimo de 12 meses. Também mostra o efeito no limite do cartão (K-12, K-13). Estouro é mostrado, nunca bloqueado.
9. **CR-9.** **Faixas (Q-C, decidida).** Valores iniciais, configuráveis por indicador:

   | Indicador | Confortável | Atenção | Crítico |
   |---|---|---|---|
   | Dívidas | abaixo de 20 % | de 20 % a 30 % | acima de 30 % |
   | Renda, bruto e líquido | abaixo de 60 % | de 60 % a 80 % | acima de 80 % |

   Os limites das faixas pertencem à faixa de atenção (20,0 % e 30,0 %; 60,0 % e 80,0 %). A comparação usa o
   percentual já arredondado a 1 casa. **Margem livre estimada negativa é sempre crítica**, qualquer que seja o
   percentual. A tela diz que as faixas são parâmetros do Klipper, não limite normativo nem garantia de saúde
   financeira.
10. **CR-10.** Itens sem data ou sem valor não entram e aparecem na lista "ficou de fora" (mesmo princípio da M-6).

## Exemplo

Receita de referência R$ 15.000,00 (manual). Despesas fixas R$ 6.500,00 por mês. Financiamento R$ 1.500,00 por mês.
Parcelas de cartão existentes R$ 1.000,00 por mês, a última contabilizada em fevereiro/2027. Gasto variável de
referência R$ 3.000,00, em categorias sem compromissos. Sem provisões, então bruto e líquido coincidem.

Simulação: TV de R$ 6.000,00 em 6× no cartão que fecha dia 3 e vence dia 10, comprada em 15/11/2026, categoria
Eletrônicos sem limite. Ela cai na fatura que fecha em 03/12/2026 e vence em 10/12/2026. Parcelas de R$ 1.000,00 de
dezembro/2026 a maio/2027.

| Mês | Dívidas | Renda | Margem livre estimada |
|---|---|---|---|
| dez/26 a fev/27 | 23,3 % atenção (era 16,7 %) | 66,7 % atenção (era 60,0 %) | R$ 2.000,00 |
| mar/27 a mai/27 | 16,7 % confortável (era 10,0 %) | 60,0 % atenção (era 53,3 %) | R$ 3.000,00 |
| jun/27 em diante | 10,0 % confortável | 53,3 % confortável | R$ 4.000,00 |

Os vencimentos de jan/27 (dia 10 é domingo, vai para 11/01) e abr/27 (sábado, vai para 12/04) mudam de dia, mas
não de mês.

## Casos de teste

```ruby
# spec/services/commitment_calculator_spec.rb
# receita: últimos 6 meses 1_800_000, 1_520_000, 1_480_000, 1_600_000, 1_500_000, 1_750_000 → 1_480_000 (fonte "conservador")
# 2 meses fechados, sem cenário nem manual → nil, motivo "receita_insuficiente"
# exemplo acima: dez/26 dívidas 23.3 atenção, renda 66.7 atenção; mar/27 16.7 confortável e 60.0 atenção;
#   jun/27 10.0 e 53.3 confortáveis
# receita 0 → indicadores nil
# assinatura de 4_990 no cartão: em dez/26 conta 1 vez em (a); a ocorrência prevista de dez sai de (c)
# pagamento de fatura de 350_000 agendado → não entra em nenhuma camada
#
# IPVA: recorrência de 360_000 em fev/27; provisão constituída 120_000; contribuição planejada 120_000 em dez e jan
#   (c) fev = 360_000 (bruto); (e) fev = 360_000; (d) dez = 120_000, jan = 120_000
#   líquido: fev contribui 0; dez e jan contribuem 120_000 cada; soma no horizonte 240_000 = 360_000 − 120_000 constituídos
#
# variável sem dupla contagem: Eletrônicos com limite 150_000 e parcela da TV de 100_000 em (a)
#   → variavel(Eletrônicos) = 50_000; com parcela de 200_000 → 0, nunca negativo
# margem livre estimada −1 centavo → faixa crítica mesmo com renda em 50,0 %
# fronteiras: 20,0 % → atenção; 19,96 % arredonda para 20,0 % → atenção; 80,0 % → atenção; 80,1 % → crítico
#
# spec/services/purchase_simulator_spec.rb
# 600_000 em 6×, compra 15/11/2026, fecha 3, vence 10 → 1ª parcela em dez/26, última em mai/27
# 100_000 em 3× → 33_334, 33_333, 33_333
# compra em 03/12/2026 (dia do fechamento) → 1ª parcela em jan/27 (K-5)
# simulação não cria Transaction, InstallmentPlan nem altera limite gravado
```

Os mesmos casos vão para `vetores/comprometimento.v1.json`, lidos pelo RSpec e pelo Vitest.

## Alteração na spec 04

Acrescentar ao fim da K-14: "As parcelas previstas alimentam o comprometimento da receita futura (spec 22, CR-2a)."
