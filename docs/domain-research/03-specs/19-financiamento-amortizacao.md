# Spec 19 — Financiamento: parcela, juros, amortização e quitação

**Origem funcional:** UXR-02 e UXR-03. Esta especificação é do Klipper; ela não reproduz o modelo de outro produto.

## Fonte da verdade

1. Conta `loan` tem `original_principal`, `opened_on`, `annual_rate`, `term_months` e `payment_frequency` mensal.
   `recorded_principal` não é digitado em cada pagamento: é a soma auditável do principal de abertura menos as
   amortizações efetivadas e mais ajustes explícitos.
2. `loan_schedule_items` materializa a previsão: vencimento, parcela, principal previsto, juros previstos e saldo
   previsto. A soma de principal do cronograma é exatamente o principal original; arredondamento segue Spec 01.
3. Um pagamento cria uma transferência atômica da conta pagadora para a conta `loan`, ligada a um
   `loan_payment_allocation`. O vínculo contém valor pago, juros, principal, encargos opcionais e saldo antes/depois.
   A soma das alocações é igual ao pagamento; principal e juros não podem ser negativos.

## Registro e alteração de parcela

4. Ao registrar uma parcela, o Klipper sugere a próxima parcela aberta do cronograma e pré-preenche principal/juros.
   A pessoa pode informar pagamento parcial ou extra, mas a confirmação sempre mostra a alocação e o novo saldo.
5. Pagamento inferior ao devido amortiza primeiro juros e encargos, depois principal. Pagamento acima do devido exige
   a escolha explícita `reduzir prazo` ou `reduzir parcela`; a projeção resultante é recalculada e preserva o plano
   original para comparação.
6. Editar valor, data, origem ou alocação altera transferência, alocação, saldo registrado e projeção numa única
   transação. Excluir uma parcela efetivada desfaz as mesmas entidades; parcela conciliada só admite reversão.
7. Nenhuma transferência para uma conta `loan` é tratada como amortização silenciosa. Se não houver alocação, ela
   fica em estado `revisar pagamento` e não altera `recorded_principal` até decisão explícita.

## Leitura e estados

8. O detalhe mostra sempre: saldo registrado, parcela seguinte e vencimento, juros/principal da próxima parcela,
   saldo previsto ao término e diferença entre previsão e registrado. Em 390 px esses cinco dados aparecem como
   lista, não como tabela horizontal.
9. Estados: `em_dia`, `vence_em_breve`, `vencido`, `pagamento_parcial`, `quitado` e `revisar_pagamento`. Texto e
   CTA explicam a próxima ação; cor não é o único indicador.
10. Falha de gravação preserva o rascunho de pagamento e não cria uma ponta isolada. Sucesso mostra uma confirmação
    com `Desfazer` enquanto o lançamento ainda não estiver conciliado.

## Casos de aceite

| Cenário | Resultado obrigatório |
|---|---|
| Parcela de R$ 222,44, com R$ 68,51 de juros e R$ 153,93 de principal | Caixa diminui R$ 222,44; principal diminui R$ 153,93; histórico e projeção mostram os mesmos valores. |
| Pagamento parcial | Juros são alocados primeiro; saldo e estado indicam parcela parcial, sem inventar quitação. |
| Pagamento extra | A tela exige reduzir prazo ou parcela e recalcula a projeção sem mudar o contrato original. |
| Falha na segunda ponta da transferência | Nenhuma ponta, alocação ou saldo é persistido; o rascunho permanece recuperável. |
| Exclusão de parcela não conciliada e desfazer | Transferência, alocação, saldo e projeção retornam exatamente ao estado anterior. |
| Pagamento importado sem detalhes | Permanece revisável e não amortiza principal até a alocação ser confirmada. |
