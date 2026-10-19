# Spec 14 — Encargos financeiros, assinaturas e débitos automáticos por conta

**Status:** rascunho de 2026-10-19, aguarda aprovação. **Origem:** backlog de 18/10, lacunas 5 e 6 (P2).
**Sprint:** junto com o D6. **Estende:** spec 05 (recorrências) e spec 04 (K-21, encargos no cartão).
**Onde mora:** `ChargesSummaryCalculator`, `SubscriptionDetector` e `AccountAutoDebitsCalculator` (services).

## Encargos e assinaturas

1. **E-1.** IOF, juros, tarifa, anuidade e seguro, **na conta ou no cartão**, vão para a categoria "Encargos
   financeiros" (a K-21 já faz isso no cartão; aqui estende à conta corrente). Casamento por regra de descrição, na
   pré-visualização, sempre editável.
2. **E-2.** Resumo mensal de encargos com o **lançamento de origem** de cada linha e o total por tipo.
3. **E-3.** **Assinatura** = recorrência detectada pelo D6 (mesmo estabelecimento, valor estável, intervalo mensal)
   com pelo menos 3 ocorrências. Mostra total mensal e data da última cobrança.
4. **E-4.** Valor que muda mais de uma faixa configurável (padrão 10 %) gera alerta "assinatura mudou de valor".
5. **E-5.** Detecção só sugere; o usuário confirma ou descarta. Descartada não volta a ser sugerida.

## Débitos automáticos por conta

6. **A-1.** Cada conta lista o que é debitado nela de forma recorrente (débito automático detectado pelo D6 ou
   marcado à mão), com valor e último débito.
7. **A-2.** "Encerrar conta" é um **checklist**, nunca uma ação: débitos a migrar, boletos com a conta cadastrada,
   parcelas futuras do cartão ligado e saldo a transferir. O app não encerra nada.
8. **A-3.** Conta com pendência no checklist mostra o motivo; sem pendência, só diz que não há nada pendente **no que
   o Klipper conhece**.

## Casos de teste

```ruby
# spec/services/charges_summary_calculator_spec.rb
# seguro do cartão 25,00 em 06/10 no Itaú → categoria Encargos financeiros, linha de origem listada
# IOF de compra internacional no Nubank → Encargos; total do mês soma por tipo
# spec/services/subscription_detector_spec.rb
# 3 cobranças mensais iguais → assinatura; 2 → não; valor sobe 15 % → alerta
# spec/services/account_auto_debits_calculator_spec.rb
# "DA ENERGISA" 469,93 em 13/10 recorrente → aparece na conta Itaú
# checklist de encerramento: 1 débito + 3 parcelas futuras → 2 pendências listadas, nada executado
```
