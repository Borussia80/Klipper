# Spec 09 — Pix e transferência para o próprio titular (detecção na importação)

**Status:** rascunho de 2026-10-19, aguarda aprovação. **Origem:** backlog de 18/10, item 1 (P0).
**Estende:** spec 03, L-7 a L-12. **Sprint:** a detecção entra no D1; o pareamento em duas linhas é o D3.
**Onde mora:** `BankImport::KindDetector` (ganha a regra de titular) e `BankImport::OwnTransferMatcher` (novo).

Sem esta regra o D1 corrige a fatura e ainda deixa transferência entre contas próprias contando como receita e
despesa (outubro: Itaú → Santander R$ 13.276,44 e Caixa → Nubank R$ 16.000).

## Regras

1. **P-1.** O usuário cadastra a identidade do titular: um ou mais **nomes** e a **máscara do CPF** como os bancos a
   imprimem (seis dígitos centrais). Fica no perfil do usuário; nunca em log nem em fixture versionada.
2. **P-2.** Uma linha de conta é **candidata a transferência própria** quando a descrição contém um nome do titular
   **e** (a máscara do CPF **ou** o rótulo de transferência do banco: "PIX TRANSF", "Transferência recebida/enviada").
   Só o nome, sem máscara nem rótulo, **não** basta (homônimo, pagamento a pessoa).
3. **P-3.** Candidata ganha `kind: transfer`, **sugerido**: aparece marcada na pré-visualização e só vira definitiva
   com a confirmação do usuário (L-12).
4. **P-4.** **Par encontrado**: outra linha candidata de sinal oposto, mesmo valor, datas a ±3 dias, contas
   diferentes do mesmo usuário → as duas viram uma transferência ligada (`transfer_pair_id`, L-7). O mesmo valor
   com mais de um par possível → pergunta, nunca escolhe.
5. **P-5.** **Ponta ausente** (conta sem extrato importado, ex.: Caixa): a linha fica `kind: transfer`, sem par, em
   estado **a ligar**. Não entra em receita nem despesa enquanto não for decidida; aparece na lista "ligar pares".
6. **P-6.** "Aplicação RDB" e "Resgate RDB" (aplicações da própria instituição) são `kind: transfer` para a conta de
   investimento, nunca despesa nem receita.
7. **P-7.** Boleto a `NU PAGAMENTOS` pago pela conta Nubank **continua despesa** (psicóloga, 13/10). O detector de
   fatura (L-12) não se amplia para esse caso: teste de regressão abaixo.
8. **P-8.** O boleto ao emissor do cartão (`PAG BOLETO ITAU UNIBANCO HOLDING`) segue ambíguo até o D4; com a fatura
   aberta de mesmo valor e mesmo banco, a pré-visualização o mostra como **provável pagamento de fatura** (D4).

## Casos de teste

```ruby
# spec/services/bank_import/own_transfer_matcher_spec.rb
# Itaú "PIX TRANSF <titular>01/10 -5.000,00" + Nubank "Transferência recebida pelo Pix <titular> <máscara> 5.000,00"
#   no mesmo dia → 1 par transfer, 0 em receita, 0 em despesa
# Pix para o titular, sem a ponta importada → transfer "a ligar"; MonthlySummary não o conta
# nome do titular sem máscara e sem rótulo de transferência → regular
# mesmo valor, dois pares possíveis → nenhum ligado, pergunta
# Nubank "Aplicação RDB -5.000,91" → transfer para a conta de investimento
# Nubank "Pagamento de boleto efetuado - NU PAGAMENTOS SA -350,00" → regular (regressão do KindDetector)
```

**Não decidido:** nada aqui altera dado já gravado; a reclassificação do histórico segue o `DRY_RUN` do D1 (Q6).
