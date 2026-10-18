# 01 — Linha de base do domínio no Klipper

Lido em 2026-10-17, `main` em `dc4c5de`. Stack real: **Nuxt 3.21** (SPA/PWA, não Nuxt 4) + **Rails 8.1** + PostgreSQL.
Fuso da aplicação: `config.time_zone = "America/Sao_Paulo"`.

## 1. Entidades

```
users ─┬─ accounts            (saldo digitado à mão)
       ├─ categories          (expense / income / transfer; natureza; reembolsada_por)
       ├─ transactions        (debit / credit / transfer; parcela n/N; parent_transaction_id)
       ├─ budgets             (limite mensal por categoria)
       ├─ investments         (cada linha = uma operação buy/sell)
       ├─ members             (portador do cartão / pessoa da família)
       ├─ net_worth_snapshots (fotografia mensal do patrimônio)
       └─ audit_logs          (eventos de exportação e autenticação)
```

### Colunas monetárias

| Tabela.coluna | Tipo | Observação |
|---|---|---|
| `accounts.balance` | `decimal(15,2)` | **Nenhuma tela edita.** `ModalNovaConta` não tem campo de saldo; só a API aceita. Na prática fica `0` |
| `accounts.saldo_fatura_atual`, `pagamento_minimo`, `iof_projetado` | `decimal(15,2)` | Digitados em `ModalEditarCartao`. Sem relação com as transações do cartão |
| `accounts.juros_rotativo_am` / `_aa` | `decimal(6,3)` / `decimal(7,3)` | Percentual |
| `transactions.amount` | `decimal(15,2)`, sempre `> 0` | O sinal vem de `transaction_type` |
| `budgets.amount_limit` | `decimal(15,2)`, `> 0` | |
| `investments.quantity` / `average_price` | `decimal(15,6)` / `decimal(15,4)` | Custo = `quantity × average_price`, sem arredondar até a soma |
| `net_worth_snapshots.*` | `decimal(14,2)` | Precisão diferente das outras (14 × 15) |

Não há ponto flutuante **no banco**. O ponto flutuante aparece na **saída**: todo calculator faz `.to_f.round(2)` e o
front soma com `parseFloat` (ver §2).

`accounts.currency` e `investments.currency` existem (padrão `BRL`), mas **nenhuma soma converte moeda**: uma conta
em USD entraria somada como se fosse real.

## 2. Onde cada cálculo é feito

| Cálculo | Backend | Frontend | Divergência |
|---|---|---|---|
| Entradas / saídas do mês | `MonthlySummaryCalculator` (`/reports/monthly`) | `useTransactions.totalDebits/totalCredits` — baixa **todas** as páginas do mês e soma com `parseFloat` | **Duplicado.** O painel usa o do front (`dashboard.vue:286-294`); o relatório usa o do back. Hoje dão o mesmo número porque as regras são iguais, mas são duas fontes de verdade |
| Saldo total das contas | `NetWorthSnapshotService.compute` soma **todas** as contas (inclusive inativas e cartões) | `useAccounts.totalBalance` soma todas; `sumCheckingBalance` exclui cartão | **Três regras diferentes** para "saldo" |
| Patrimônio | `NetWorthSnapshotService.compute` = Σ saldos + custo dos investimentos | — | Usa saldo digitado (≈ 0) e custo, não valor de mercado |
| Orçamento gasto / restante | `BudgetEngine` | `useBudgetKpis` soma as linhas que o back devolve | Soma de agregados: ok |
| % gasto da renda | — | `pctOfIncome` no front | Só front |
| Divisão por natureza | `NaturezaSplitCalculator` | — | Ok |
| Encargos do cartão | `DebtRankingCalculator` (juros sobre `saldo − mínimo`) | `sumDebtCharges` | Ok |
| Valor de posição | — | `investimentos.vue:80`: `quantity × average_price` com `parseFloat` | Só front, e é custo |
| Cobertura de reembolso | `ReimbursementCoverageCalculator` | — | Ok |

## 3. Como os saldos são obtidos

- **Saldo de conta:** coluna `accounts.balance`, **digitada**, nunca derivada das transações. Como nenhuma tela a
  edita, o saldo exibido em `/contas` é `R$ 0,00` para quem não usou a API.
- **Saldo histórico:** não existe.
- **Patrimônio histórico:** `net_worth_snapshots`, gravado pelo job `RecordNetWorthSnapshotsJob` no dia 1 de cada mês
  (`config/recurring.yml`, `5 0 1 * *`). O Render Free hiberna e o uso hoje é local: o job **não roda** se o processo
  não estiver de pé à 00:05.
- **Fatura do cartão:** `saldo_fatura_atual`, digitada.

## 4. Cobertura de testes das regras financeiras

53 arquivos de spec no backend. Bem cobertos: importação (PDF, CSV, parser de valor, hash), relatórios (56 exemplos
em `reports_spec`), reembolso, recorrência de categoria, patrimônio (inclusive o backfill do FIN-002), ranking de
dívida.

Sem cobertura **porque a regra não existe**: saldo derivado, transferência, fatura por fechamento, parcelas futuras,
conversão de moeda, estorno, split, arredondamento de rateio.

Cobertura que **fixa o comportamento errado** (ver §5): `nubank_fatura_adapter_spec.rb:27-49` espera que
"Pagamento em 10 JUN" vire linha de crédito; `transaction_writer_spec.rb:28` espera que uma segunda linha idêntica
seja descartada, sem distinguir "reimportação" de "duas compras iguais no mesmo dia".

## 5. Riscos encontrados, do mais grave ao menos grave

| # | Risco | Evidência | Efeito |
|---|---|---|---|
| R1 | **Pagamento de fatura vira receita.** A fatura importada traz "Pagamento em DD MMM" como crédito, e o `AutoCategorizerService` casa `/pagamento/` com a categoria "Renda". No extrato da conta corrente o mesmo pagamento entra como débito | `nubank_fatura_adapter.rb:30,59,83`; `auto_categorizer_service.rb:9` | Receita inflada pelo valor da fatura **e** despesa contada duas vezes (a compra na fatura + o pagamento no extrato). Distorce painel, orçamento, % da renda e natureza |
| R2 | **Compras iguais no mesmo dia são descartadas.** O hash de deduplicação é `usuário + conta + data + descrição + valor + tipo`; a segunda linha idêntica **do mesmo arquivo** vira "duplicada" | `bank_import/dedupe_hash.rb`, `transaction_writer.rb` | Perda silenciosa de dado (dois cafés, duas corridas de Uber) |
| R3 | **Reimportar depois de "atribuir conta" duplica tudo.** `assign_account` muda `account_id` mas não recalcula `dedupe_hash`; o hash antigo tem conta nula | `transactions_controller.rb:39-48` | As 345 linhas do UR-2 voltam em dobro se o extrato for reimportado com conta |
| R4 | **Saldo não existe.** `balance` é digitado e não há tela para digitar; patrimônio = custo dos investimentos | §3 | Patrimônio, herói do painel (Fatia 3 de UX) e detalhe de conta (Fatia 4) não têm número confiável |
| R5 | **Patrimônio soma contas arquivadas e soma cartão como ativo.** `user.accounts.sum(:balance)` sem `.active` e sem distinguir passivo | `net_worth_snapshot_service.rb:14` | Se alguém lançar o saldo do cartão como positivo, o patrimônio sobe com a dívida |
| R6 | **Estorno conta como receita e não abate o gasto.** Estorno é `credit`; orçamento só soma `debit` da categoria | `budget_engine.rb:12`; `monthly_summary_calculator.rb` | Orçamento estourado que já foi devolvido; renda inflada |
| R7 | **Data futura proibida.** `occurred_on_not_in_future` em `Transaction` e `Investment` | `transaction.rb:35` | Impede parcela futura, agendado e lançamento previsto: a base de cartão e de fluxo projetado |
| R8 | **Parcelas soltas.** Só `installment_number/total` por linha, sem vínculo entre elas; o leitor da fatura Itaú ignora "Próximas faturas" | `itau_fatura_adapter.rb:76` | Limite disponível e compromisso futuro do cartão não são calculáveis |
| R9 | **Split latente com dupla contagem.** `parent_transaction_id` existe, nada cria split, e nenhum calculator exclui o pai | `transaction.rb:7-9` | Se o split for ligado sem regra, o gasto dobra |
| R10 | **Duas fontes de verdade no painel** (§2) | `dashboard.vue:286` | Risco de divergência quando uma regra mudar só de um lado |
| R11 | **Corrida na deduplicação.** `exists?` e depois `create!`, com índice **não único** em `(user_id, dedupe_hash)` | `transaction_writer.rb` | Duas importações simultâneas gravam a mesma linha. Baixa probabilidade (usuário único) |
| R12 | **Moeda ignorada nas somas** | §1 | Sem efeito hoje (tudo BRL); vira bug no primeiro cartão internacional em USD |
| R13 | **Cron sem fuso explícito.** `5 0 1 * *` depende do fuso do processo; em UTC o job roda às 21:05 do último dia do mês anterior em São Paulo, e `Date.current` cai no mês anterior | `config/recurring.yml` | A confirmar: snapshot pode ser gravado no mês errado. Hoje o job nem roda (local) |
| R14 | **Ponto flutuante na borda.** `.to_f` em toda resposta e `parseFloat` + `reduce` no front | §2 | Erro de centavo raro na exibição; some quando o front parar de somar |

## 6. O que já está certo e deve ser preservado

- Dinheiro em `decimal` no banco e `BigDecimal` no Ruby.
- `AmountParser` com os dois formatos (BR e en-US) e testes.
- Linha de PDF assinada (`RowSigner`): o cliente não altera valor, data ou descrição entre preview e confirmação.
- Calculators extraídos dos controllers (ARCH-006) e queries fixas (sem N+1) nos relatórios.
- `parseISODate` no front com meio-dia, evitando a virada de data por UTC.
- `Investment` como ledger de operações (não saldo agregado), com sinal de venda numa fonte só (FIN-002).
