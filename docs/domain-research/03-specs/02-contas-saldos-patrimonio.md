# Spec 02 — Contas, saldos, reconciliação e patrimônio

**Onde mora:** `AccountBalanceCalculator` (service, consulta) para saldo; `ReconciliationService` (service,
transacional) para conferência; `NetWorthCalculator` substitui o `compute` do `NetWorthSnapshotService`.

## Tipos de conta

1. **C-1.** `account_type` passa a ser:

| Tipo | Natureza | Hoje |
|---|---|---|
| `checking` (corrente) | ativo | existe |
| `digital` | ativo | existe; tratar igual a `checking` |
| `savings` (poupança) | ativo | existe |
| `cash` (carteira / dinheiro) | ativo | **novo** |
| `investment` | ativo | existe |
| `receivable` (valores a receber) | ativo | **novo** |
| `credit_card` | **passivo** | existe |
| `loan` (empréstimo / dívida) | **passivo** | **novo** |

2. **C-2.** A natureza (ativo / passivo) é derivada do tipo, numa constante do model. Não é coluna.

## Saldo

3. **C-3.** **O saldo é derivado, não digitado.**

```
saldo(conta, D) = saldo_inicial(conta)
                + Σ valor_com_sinal(t)   para t ∈ lançamentos da conta,
                                          status ∈ {efetivado, conciliado},
                                          t.occurred_on ≤ D,
                                          t não é pai de split
valor_com_sinal(t) = +amount se t entra na conta (credit, transfer_in)
                     −amount se t sai da conta  (debit, transfer_out)
```

   Em conta **passivo** a mesma fórmula dá saldo negativo quando há dívida: compra no cartão é `debit`
   (saldo −), pagamento da fatura é `transfer_in` (saldo +). Um cartão com R$ 1.200 em compras e R$ 800 pagos tem
   saldo **−400**, que é o que se deve.

4. **C-4.** `saldo_inicial` e `saldo_inicial_em` (data) são colunas novas. Lançamento anterior a `saldo_inicial_em`
   é recusado na criação manual e avisado na importação ("anterior ao saldo inicial; não entra no saldo"), porque
   o saldo inicial já o contém.
5. **C-5.** Saldo **previsto** (para fluxo de caixa) = mesma fórmula incluindo `status = previsto`.
6. **C-6.** A coluna `accounts.balance` deixa de ser lida. Fica no banco até a Sprint D2 terminar (migração em dois
   passos, ver `04-modelo-dados.md`).

## Reconciliação

7. **C-7.** O usuário informa `saldo_banco` numa data `D`. O sistema calcula `saldo(conta, D)` e mostra a diferença.
8. **C-8.** Ao confirmar com diferença ≠ 0, cria **um lançamento de ajuste** (`kind: adjustment`, sem categoria,
   fora de orçamento e de receitas/despesas) com valor = diferença, na data `D`, e marca como `conciliado` todo
   lançamento efetivado da conta com `occurred_on ≤ D`.
9. **C-9.** Lançamento conciliado não pode ter valor, data ou conta alterados sem antes "desconciliar" (ação
   explícita, registrada). Categoria e descrição podem mudar.
10. **C-10.** A primeira reconciliação de uma conta migrada (saldo inicial 0) é o caminho para o Roberto acertar os
    saldos reais: em vez de digitar saldo, ele concilia uma vez.
10a. **C-10a.** Reconciliação só em data **posterior** à última conciliação da conta. Para corrigir uma data
    anterior, o usuário primeiro desconcilia as posteriores (ação explícita e registrada). Assim uma correção antiga
    nunca altera em silêncio um saldo já conferido, e o saldo atual muda só pelo ajuste visível.
10b. **C-10b.** Cada reconciliação fica gravada (`reconciliations`: data, saldo do banco, diferença, ajuste criado,
    usuário) e não é apagada ao desconciliar: ganha `undone_at`.

## Arquivar

11. **C-11.** Arquivar (`active: false`, já existe) **não apaga nada** e mantém o saldo no histórico.
12. **C-12.** Só pode arquivar com saldo zero, ou criando o ajuste que zera (com confirmação). Conta arquivada sai do
    patrimônio **atual** mas continua nos **pontos passados** da série.
13. **C-13.** Excluir de verdade só conta sem nenhum lançamento. Conta com transferências não pode ser excluída
    (a outra ponta ficaria órfã); só arquivada.

## Patrimônio

```
patrimônio(D) = Σ saldo(c, D) para c ativo     ← inclui o valor das posições (spec D9) quando houver
              + Σ saldo(c, D) para c passivo   ← já negativo
```

14. **C-14.** Conta arquivada antes de `D` entra com o saldo que tinha em `D` (zero, por C-12).
15. **C-15.** Enquanto não houver valor de mercado (D9), investimento entra pelo custo, com o rótulo "custo" na tela
    (já é assim).
16. **C-16.** `net_worth_snapshots` vira **cache recalculável**: o job grava, mas um recálculo a partir do ledger pode
    reescrever qualquer mês. Fica a regra do FIN-002: uma fórmula só (`NetWorthCalculator`), usada pelo snapshot e
    pela tela.

## Exemplo resolvido

Conta corrente com saldo inicial R$ 2.000,00 em 01/10. Lançamentos: 05/10 salário +5.000,00; 06/10 mercado
−350,00; 10/10 pagamento da fatura (transferência para o cartão) −1.200,00; 15/10 aluguel previsto −2.500,00.

- `saldo(10/10)` = 2.000 + 5.000 − 350 − 1.200 = **5.450,00**
- `saldo_previsto(31/10)` = 5.450 − 2.500 = **2.950,00**
- Banco informa 5.430,00 em 10/10 → ajuste de **−20,00** (tarifa esquecida); os três lançamentos até 10/10 e o ajuste ficam
  conciliados.

Cartão com compras de 1.200,00 em setembro e o pagamento acima: saldo em 10/10 = −1.200 + 1.200 = **0**.
Patrimônio em 10/10 = 5.450 + 0 = 5.450 (antes do ajuste).

## Casos de borda

| Caso | Regra |
|---|---|
| Lançamento sem conta (as 345 do UR-2) | Fora de qualquer saldo; o `DataHealthBanner` já avisa. Não entram no patrimônio |
| Transferência para conta arquivada | Recusada |
| Lançamento retroativo em mês conciliado | Permitido, mas a conta mostra "saldo diverge da última conciliação" |
| Conta em USD | Saldo na moeda da conta; patrimônio converte (spec 01, D-11) |
| Split | Só os filhos entram (o pai é excluído) |

## Casos de teste (RSpec)

```ruby
# spec/services/account_balance_calculator_spec.rb
# corrente, saldo_inicial 2000 em 01/10 + os 4 lançamentos do exemplo
saldo(conta, Date.new(2026,10,10))                       # => 5450.00
saldo(conta, Date.new(2026,10,31), incluir_previstos: true) # => 2950.00
saldo(conta, Date.new(2026,9,30))                        # => 2000.00 (antes de qualquer lançamento)
saldo(cartao, Date.new(2026,10,10))                      # => 0.00
# split: pai 100 com filhos 60 + 40 → saldo varia 100, não 200
# conta passivo sem pagamento: compras 300 → saldo -300

# spec/services/reconciliation_service_spec.rb
ReconciliationService.call(conta, on: Date.new(2026,10,10), bank_balance: 5430) # cria ajuste -20; 3 + ajuste conciliados; previsto de 15/10 intocado
# diferença zero → não cria ajuste, concilia
# lançamento conciliado: update(amount:) → erro; update(category_id:) → ok

# spec/services/net_worth_calculator_spec.rb
# conta arquivada em agosto: entra no ponto de julho, não no de outubro
# cartão com saldo -400 reduz o patrimônio em 400 (corrige R5)
# snapshot e tela dão o mesmo número (mesma classe)
```
