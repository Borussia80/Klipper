# Spec 21 — Provisionamento voluntário

**Status:** rascunho de 2026-11-19, revisão 2 (ressalvas da revisão de 19/11 incorporadas), aguarda aprovação.
**Domínio:** Financial Planning (ADR-2026-11-19-007).
**Depende de:** spec 02 (saldo derivado), spec 01 (D-1 a D-4, dinheiro), spec 04 (fatura), spec 05 (recorrências),
spec 11 (custo de resgate). **Alimenta:** spec 22 (camadas d e e). **Onde mora:** `Provision`, `ProvisionEntry` e
`ProvisionCalculator` (service puro).

Separar dinheiro que já existe para uma finalidade futura (IPVA, férias, manutenção), com o benefício do envelope e
sem obrigar a alocar toda a renda.

## Conceitos distintos

| Conceito | O que é | Onde vive |
|---|---|---|
| Meta | Intenção de economizar | Kakebo, spec 12 |
| Provisão | Dinheiro existente e líquido reservado para uma finalidade | esta spec |
| Investimento | Aplicação efetiva de recursos | specs 11, 18, 20 |

## Invariantes

1. Provisão **não é despesa**: não cria `transaction`, não entra em `countable`, não muda o gasto da spec 08.
2. Provisão **não é transferência**: nenhum saldo de conta muda.
3. Provisão **não altera o patrimônio líquido** (spec 02, spec 20).
4. Provisão **constituída** reduz os recursos livres.
5. Provisão **planejada** compromete a margem futura (spec 22), mas não reduz os recursos livres de hoje.
6. A despesa realizada consome a provisão correspondente uma única vez, sem dupla contagem.
7. Liquidez não é patrimônio: só dinheiro disponível até a data da finalidade serve de lastro.

## Regras

1. **PV-1.** Uma provisão tem `nome`, `meta` (centavos, opcional), `data_alvo` (opcional), `conta_lastro_id`
   (opcional; nulo = total das contas elegíveis), `recurrence_id` (opcional) e `arquivada`.
2. **PV-2.** O saldo da provisão é derivado de um livro próprio (`ProvisionEntry`) com cinco tipos: `constituir` (+),
   `liberar` (−), `reservar_fatura` (−), `consumir` (−) e `restaurar` (+). Todo `reservar_fatura`, `consumir` e
   `restaurar` aponta para o lançamento ou o estorno que o originou. Nenhum saldo é campo editável.
3. **PV-3.** **Lastro, validado nas duas condições ao mesmo tempo:**
   - por conta: para cada conta X, Σ provisões com lastro em X ≤ saldo elegível(X);
   - global: Σ **todas** as provisões ≤ Σ saldo elegível de todas as contas.
   Constituir algo que viole qualquer uma das duas é recusado com 422, e a mensagem diz quanto está livre em cada
   condição.
4. **PV-4.** **Conta elegível como lastro** (PV-3): conta corrente, poupança e carteira entram pelo saldo. Conta de
   investimento só entra se o resgate estiver disponível até a `data_alvo` (ou em D+0, sem data), pelo valor líquido
   do custo de resgate (spec 11). Valor de mercado (spec 18) nunca é lastro. Um CDB que vence em 2031 não cobre o
   IPVA de fevereiro.
5. **PV-5.** **Recursos livres** seguem a C-17 da spec 02: saldo das contas líquidas − provisões
   constituídas − reservas de fatura − parte não reservada das faturas fechadas e não quitadas. O valor pode ser
   negativo.
6. **PV-6.** **Provisão descoberta.** Se o saldo elegível cair abaixo de provisões + reservas, a tela mostra
   "descoberta: R$ X". Nada é liberado automaticamente; a decisão é do usuário.
7. **PV-7.** **Consumo à vista** (débito, Pix, dinheiro). Um lançamento de despesa pode ser marcado com
   `provision_id`. Consome `min(valor, saldo_provisao)`. O excedente é gasto comum. Consumo parcial é permitido.
8. **PV-8.** **Consumo no cartão.** A compra marcada com `provision_id` não devolve o valor aos recursos livres,
   porque a dívida continua aberta. O valor coberto, `min(valor, saldo_provisao)`, passa de provisão para
   **reserva de fatura**, ligada à fatura em que o item cai (K-5). Quando o pagamento dessa fatura é registrado, a
   reserva vira `consumir`, e o saldo da conta pagadora cai pelo próprio pagamento. Pagamento parcial da fatura
   consome a reserva na mesma proporção, arredondada pela D-4.
9. **PV-9.** **Estornos, idempotentes.** Excluir o lançamento reverte todo o consumo ou a reserva. Estorno parcial de
   valor V restaura `min(V, consumido_restante)` à provisão. Cada reversão é chaveada pelo id do lançamento ou do
   estorno: processar o mesmo evento duas vezes não muda nada. Editar o valor recalcula pela PV-7 ou PV-8.
10. **PV-10.** **Liberar** devolve valor aos recursos livres sem mexer em saldo de conta. Liberar mais que o saldo
    da provisão é recusado.
11. **PV-11.** **Plano mensal (intenção).** `contribuicao_planejada` mensal é intenção, não provisão: não passa pela
    PV-3, não reduz recursos livres e só alimenta a spec 22 (camada d). A sugestão é
    `(meta − saldo) ÷ meses até data_alvo`, dividida pela D-4. É exibida, nunca gravada sozinha.
12. **PV-12.** **Recorrência vinculada.** Com `recurrence_id`, a cobertura (spec 22, camada e) é alocada às
    ocorrências futuras **em ordem de data**: o saldo projetado (constituído + contribuições planejadas até a data)
    cobre primeiro a ocorrência mais próxima, e só o que sobra passa para a seguinte. O mesmo real nunca cobre duas
    ocorrências.
13. **PV-13.** **Orçamento (Q-A, decidida).** A despesa paga com provisão conta **integralmente** no gasto do mês
    (spec 08, O-1). A provisão financia a despesa, mas não muda sua natureza. A tela mostra quanto da despesa foi
    coberto pela provisão.
14. **PV-14.** **Kakebo (Q-B, decidida).** Ao fechar o mês com meta de economia atingida, o app **oferece** três
    destinos: constituir provisão, registrar aporte em investimento ou manter como recurso livre. Nada é convertido
    sem confirmação.
15. **PV-15.** Dinheiro em centavos inteiros na API, pelo contrato de dinheiro decidido em 19/11/2026 (adendo da
    spec 01, ainda não integrado). Percentual de meta só para exibição,
    calculado a partir de centavos, com 0 casas e meio-par.

## Exemplo

Saldo elegível R$ 10.000,00. Provisões: IPVA 1.200 (meta 3.600), Férias 1.800 (meta 6.000), Manutenção 1.000
(meta 2.000). Recursos livres: **6.000,00**. Metas: 33 %, 30 %, 50 %.

Compra de R$ 2.000,00 no cartão, coberta por provisão de R$ 2.000,00, com saldo de R$ 10.000,00:

| Momento | Saldo | Provisão | Reserva de fatura | Livres |
|---|---|---|---|---|
| Antes da compra | 10.000 | 2.000 | 0 | 8.000 |
| Após a compra no cartão | 10.000 | 0 | 2.000 | 8.000 |
| Após o pagamento da fatura | 8.000 | 0 | 0 | 8.000 |

## Casos de teste

```ruby
# spec/services/provision_calculator_spec.rb
# saldo 1_000_000; provisões 120_000 + 180_000 + 100_000 → livres 600_000; PL inalterado
# constituir 700_000 com livres 600_000 → 422, mensagem "livre: R$ 6.000,00"
# lastro por conta: conta A 200_000, conta B 800_000; provisão em A de 250_000 → 422 (falha por conta)
# lastro global: A 200_000 com provisão 200_000 em A; B 100_000; provisão sem conta de 150_000 → 422 (global 300_000 < 350_000)
# investimento: CDB que vence em 2031, data_alvo fev/27 → não é elegível
# investimento: liquidez diária 50_000, custo de resgate 0 → elegível por 50_000
#
# à vista: despesa IPVA 360_000 marcada com provisão IPVA (120_000)
#   consome 120_000; provisão 0; saldo 640_000; provisões 280_000; livres 360_000
#   gasto do mês no orçamento: 360_000 integral; coberto por provisão: 120_000
# estorno parcial de 50_000 dessa despesa → provisão IPVA 50_000
# processar o mesmo estorno outra vez → provisão IPVA continua 50_000
# excluir a despesa → provisão IPVA volta a 120_000
#
# cartão: saldo 1_000_000, provisão 200_000; compra de 200_000 marcada
#   provisão 0; reserva_fatura 200_000; saldo 1_000_000; livres 800_000
#   pagamento da fatura → saldo 800_000; reserva 0; livres 800_000
# cartão parcial: compra de 200_000 com provisão 120_000 → reserva 120_000; 80_000 é dívida comum
# pagamento de metade da fatura → consome 60_000 da reserva; reserva 60_000
#
# saldo cai para 300_000 com provisões 400_000 → livres −100_000; descoberta 100_000; nada liberado
# liberar 150_000 da Manutenção (saldo 100_000) → recusado
# recorrência trimestral de 100_000 em jan e abr, provisão 120_000, sem contribuições:
#   jan coberta 100_000; abr coberta 20_000, não coberta 80_000
# sugestão: meta 100_000, saldo 0, 3 meses → 33_334 + 33_333 + 33_333 (D-4, resto na primeira)
# nenhuma operação de provisão cria Transaction nem altera Account#balance
```

Os mesmos casos vão para `vetores/provisao.v1.json`, lidos pelo RSpec e pelo Vitest.
