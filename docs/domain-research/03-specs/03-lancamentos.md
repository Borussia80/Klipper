# Spec 03 — Lançamentos: tipos, transferência, status, estorno, split

**Onde mora:** validações no model `Transaction`; criação de transferência e estorno em `TransferService` e
`RefundService` (transacionais, as duas pontas ou nada); regra de "o que conta como receita/despesa" num **scope
único** `Transaction.countable` usado por **todo** calculator.

## Tipos

1. **L-1.** `transaction_type` continua `debit` / `credit`. Entram dois campos:
   - `kind`: `regular` · `transfer` · `refund` · `adjustment` · `card_payment` (default `regular`)
   - `status`: `previsto` · `efetivado` · `conciliado` (default `efetivado`). "Pendente" não entra: no Brasil não há
     compensação de cheque no uso do Roberto, e a compra no cartão já é efetivada na data da compra.
2. **L-2.** O valor `transfer` de `transaction_type` (hoje sem uso) é migrado para `kind: transfer` e removido do
   enum.

## A regra que corrige tudo: o que conta

```
Transaction.countable = kind ∈ {regular, refund}
                        AND status ≠ previsto
                        AND NOT (é pai de split)
```

3. **L-3.** Receita do mês = Σ `credit` countable com `kind = regular`.
4. **L-4.** Despesa do mês = Σ `debit` countable `regular` **−** Σ `refund` (estorno abate a despesa da categoria,
   não vira receita). Corrige R6.
5. **L-5.** `transfer`, `card_payment` e `adjustment` **nunca** entram em receita, despesa, orçamento, natureza ou
   % da renda. Entram no **saldo** das contas (spec 02). Corrige R1.
6. **L-6.** Todo calculator (`MonthlySummaryCalculator`, `MonthlySeriesCalculator`, `BudgetEngine`,
   `NaturezaSplitCalculator`, `CategoryRecurrenceCalculator`, `ReimbursementCoverageCalculator`) passa a partir de
   `countable`. Um spec compartilhado (`it_behaves_like "ignora transferências"`) roda contra cada um.

## Transferência entre contas próprias

7. **L-7.** Uma transferência é **duas linhas** ligadas por `transfer_pair_id` (FK para a outra linha):
   `debit` na origem, `credit` no destino, mesmo valor, mesma data, as duas com `kind: transfer`, sem categoria.
   (Desenho de duas linhas espelhadas, como no ezBookkeeping; ver `04-modelo-dados.md` sobre por que não um ledger.)
8. **L-8.** Criar, editar valor/data e excluir mexem nas duas linhas na mesma transação de banco. Editar a
   descrição de uma ponta não muda a outra.
9. **L-9.** Origem ≠ destino; as duas contas do mesmo usuário e ativas.
10. **L-10.** Moedas diferentes: cada ponta tem o valor na moeda da sua conta; `fx_rate` = destino / origem,
    guardado na ponta de destino.
11. **L-11.** **Pagamento de fatura** é uma transferência da corrente para o cartão com `kind: card_payment` nas duas
    pontas (o tipo próprio serve para a fatura saber que foi paga, spec 04).
12. **L-12.** **Detecção na importação** (só sugere, o usuário confirma na pré-visualização):
    - linha de fatura cuja descrição casa `/^pagamento (em|recebido|efetuado)/i`, ou seção "Pagamentos" do Nubank →
      marcada `card_payment`;
    - linha de extrato de corrente que casa `/pagto.*cart|fatura|pag(amento)? cart[aã]o/i` → `card_payment`;
    - quando as duas pontas existem (mesmo valor, datas a ±3 dias, uma em cartão e outra em corrente), o sistema
      **liga** as duas em vez de criar uma terceira;
    - o `AutoCategorizerService` deixa de casar `/pagamento/` com "Renda" (a palavra está nas duas pontas do cartão).

## Status

13. **L-13.** `previsto` permite data futura. A validação `occurred_on_not_in_future` passa a valer **só** para
    `efetivado` / `conciliado`. Corrige R7 sem abrir a porta para efetivado no futuro.
14. **L-14.** Prevista vira efetivada por ação do usuário ou por conciliação com uma linha importada (spec 06).
15. **L-15.** Conciliado: ver spec 02, C-9.

## Estorno e reembolso

16. **L-16.** **Estorno** (o estabelecimento devolve): `kind: refund`, `credit`, mesma conta, mesma categoria da compra,
    `refund_of_id` opcional apontando para a compra. Abate a despesa da categoria no mês **do estorno** (competência
    do estorno, não da compra), porque é quando o dinheiro volta.
17. **L-17.** Estorno sem compra ligada (importado) recebe a categoria pela regra normal e o `kind` pela detecção
    `/estorno|reembolso|devolu/i`.
18. **L-18.** **Reembolso de terceiro** (plano de saúde, empresa): continua como hoje — receita na categoria de
    reembolso, ligada pela `reimbursed_by_category_id`, e o `ReimbursementCoverageCalculator` mede a cobertura.
    Não é estorno: o dinheiro vem de outra fonte e é renda para fins de fluxo de caixa.
19. **L-19.** "Valor que alguém me deve" (dividi a conta do jantar): conta `receivable` (spec 02). A parte do outro é
    uma transferência da corrente para a conta a receber; quando ele paga, transferência de volta. A despesa do
    Roberto é só a parte dele.

## Split (importante)

20. **L-20.** Pai guarda o total e **não conta** (fora de `countable`). Filhos têm categoria, valor e herdam conta, data
    e status. Σ filhos = pai, validado no serviço (o model não vê os irmãos de forma confiável).
21. **L-21.** Split por percentual usa `Money.split` com resto na última parte (spec 01, D-4).

## Casos de borda

| Caso | Regra |
|---|---|
| Excluir uma ponta de transferência | Exclui as duas, com aviso |
| Conta excluída com transferências | Proibido; só arquivar (spec 02, C-13) |
| Estorno maior que a compra no mês (compra em setembro, estorno em outubro) | Despesa líquida da categoria em outubro fica **negativa**; o orçamento mostra "crédito de R$ X" em vez de 0 % |
| Pagamento de fatura importado só da fatura (sem extrato) | Fica `card_payment` sem par, fora de receita; aviso "falta a outra ponta" |
| Transferência entre moedas | L-10 |

## Casos de teste (RSpec)

```ruby
# shared_examples "ignora transferências" — roda em cada calculator
# dado: salário 5000 (credit regular), mercado 350 (debit regular), transferência 1200 corrente→cartão,
#       compra no cartão 1200 (debit regular), estorno 50 (refund)
MonthlySummaryCalculator: total_credits => 5000.00, total_debits => 1500.00 (350 + 1200 − 50)
BudgetEngine(categoria do mercado, limite 400): spent => 350.00
NaturezaSplitCalculator: total => 1500.00

# spec/services/transfer_service_spec.rb
TransferService.call(from: corrente, to: cartao, amount: 1200, on: d) # => 2 linhas, pair ligado, sem categoria
# falha na segunda linha → nenhuma gravada
# update(amount: 1300) numa ponta → as duas com 1300
# from == to → erro; conta de outro usuário → 404

# spec/models/transaction_spec.rb
build(:transaction, status: "previsto", occurred_on: 1.month.from_now).valid?  # => true
build(:transaction, status: "efetivado", occurred_on: 1.day.from_now).valid?   # => false

# spec/services/pdf_adapters/nubank_fatura_adapter_spec.rb (ajuste do existente)
"Pagamento em 10 JUN" => kind: "card_payment" (hoje: credit regular)
# spec/services/auto_categorizer_service_spec.rb
AutoCategorizerService.call("Pagamento em 10 JUN", user) # => nil (hoje: Renda)
```
