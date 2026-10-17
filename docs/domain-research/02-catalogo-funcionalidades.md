# 02 — Catálogo de funcionalidades

Legenda da situação: **existe** · **parcial** · **não existe**. Prioridade: **essencial** (sem ela os números do app
estão errados ou o uso brasileiro básico não fecha) · **importante** (muda decisão, mas o app é correto sem ela) ·
**desejável**.

Sobre as referências: ezBookkeeping e Actual foram lidos no código (MIT). Do Sure e do Cashew só há o que os READMEs
públicos dizem; **nenhuma interface foi observada em execução nesta rodada** (as URLs do Sure e do ezBookkeeping não
foram fornecidas, e o PWA do Cashew não foi aberto). Ver `06-registro-pi.md`.

## Tabela de situação e prioridade

| Módulo | Item | Situação | Prioridade | Spec |
|---|---|---|---|---|
| Fundamentos | Representação monetária e política de arredondamento | parcial | essencial | `03-specs/01` |
| Fundamentos | Moeda por conta e câmbio (PTAX, taxa travada) | parcial (coluna sem uso) | importante | `03-specs/01` §moeda |
| Fundamentos | Datas: competência × caixa, fuso, sem horário | parcial | essencial | `03-specs/01` |
| Contas | Tipos (corrente, poupança, carteira, cartão, investimento, dívida, a receber) | parcial (5 tipos, sem dívida/a receber/dinheiro) | essencial | `03-specs/02` |
| Contas | Saldo inicial, atual e histórico | não existe (saldo digitado) | essencial | `03-specs/02` |
| Contas | Reconciliação com saldo do banco | não existe | essencial | `03-specs/02` |
| Contas | Arquivar sem perder histórico | parcial (`active`, mas o patrimônio soma arquivada) | essencial | `03-specs/02` |
| Lançamentos | Receita, despesa, **transferência entre contas próprias** | parcial (tipo `transfer` sem par e sem uso) | essencial | `03-specs/03` |
| Lançamentos | Split em várias categorias | parcial (coluna sem regra) | importante | `03-specs/03` §split |
| Lançamentos | Status prevista / efetivada / conciliada | não existe | essencial | `03-specs/03` |
| Lançamentos | Estornos e reembolsos | parcial (reembolso por categoria; estorno sem vínculo) | essencial | `03-specs/03` |
| Lançamentos | Tags, anexos, observações | parcial (só `notes`) | desejável | — |
| Lançamentos | Histórico de alterações | parcial (`audit_logs` só para exportação/auth) | importante | `05-plano` |
| Cartão | Fatura: fechamento, vencimento, melhor dia | não existe | essencial | `03-specs/04` |
| Cartão | Parcelado: geração, resto dos centavos, com/sem juros, antecipação | parcial (número/total por linha) | essencial | `03-specs/04` |
| Cartão | Limite total, usado e disponível com parcelas futuras | não existe | essencial | `03-specs/04` |
| Cartão | Pagamento de fatura como transferência, parcial, rotativo | não existe (pagamento vira receita — R1) | essencial | `03-specs/04` |
| Cartão | Compra internacional com IOF e câmbio | parcial (`iof_projetado` digitado) | importante | `03-specs/04` §internacional |
| Cartão | Estorno em fatura aberta e futura | não existe | essencial | `03-specs/04` |
| Recorrências | Regras (mensal, dia útil, último dia, intervalo) | não existe | essencial | `03-specs/05` |
| Recorrências | Previstas e confirmação | não existe | essencial | `03-specs/05` |
| Recorrências | "Só esta" × "esta e as próximas" | não existe | importante | `03-specs/05` |
| Categorias | Dois níveis | não existe (Fatia 1 de UX, já aprovada) | essencial | `docs/ux-research/05-specs/07` |
| Categorias | Motor de regras (condição → ação) com prioridade | parcial (8 regex fixas) | essencial | `03-specs/07` |
| Categorias | Aprendizado com correções | não existe | importante | `03-specs/07` §aprendizado |
| Importação | PDF | existe (Itaú, Nubank, BTG) | — | — |
| Importação | CSV | existe (cabeçalho por alias) | — | — |
| Importação | OFX | não existe | importante | `03-specs/06` |
| Importação | Deduplicação por ID externo e aproximada | parcial (hash exato, com R2 e R3) | essencial | `03-specs/06` |
| Importação | Conciliar com previstas | não existe | importante | `03-specs/06` |
| Importação | Mapeamento de colunas e pré-visualização | parcial (preview só no PDF) | importante | `03-specs/06` |
| Importação | Desfazer importação | não existe | essencial | `03-specs/06` |
| Orçamento | Mensal por categoria | existe | — | `03-specs/08` |
| Orçamento | Envelope × limite | limite | essencial (decisão) | `03-specs/08` |
| Orçamento | Rollover, estouro, alertas | parcial (estouro na tela) | importante | `03-specs/08` |
| Orçamento | Período customizado | não existe | desejável | — |
| Planejamento | Fluxo de caixa projetado | não existe | importante | `05-plano` D9 |
| Planejamento | Metas com prazo e aporte | não existe | importante | `05-plano` D9 |
| Planejamento | Simulação de quitação de dívida | parcial (ranking de encargos) | importante | `05-plano` D9 |
| Patrimônio | Patrimônio no tempo (ativos − passivos) | parcial (snapshot mensal sobre saldo digitado) | essencial | `03-specs/02` §patrimônio |
| Investimentos | Rentabilidade simples / TWR / MWR | não existe | importante | `05-plano` D9 |
| Investimentos | % do CDI e real (IPCA) com SGS | não existe | importante | `05-plano` D9 |
| Investimentos | Atualização manual de valor | não existe (só custo) | importante | `05-plano` D9 |
| Relatórios | Receitas × despesas por período / categoria / conta | parcial (mês e série; sem conta) | importante | — |
| Relatórios | Evolução de patrimônio | existe (snapshots) | — | — |
| Relatórios | Recorrentes e assinaturas detectadas | parcial (`CategoryRecurrenceCalculator` por categoria) | desejável | — |
| Relatórios | Exportação CSV / OFX | não existe | desejável | — |

## Como as referências resolvem (resumo por módulo)

**Transferência.** ezBookkeeping grava a transferência como **duas linhas espelhadas** (saída na conta de origem,
entrada na de destino) ligadas por `RelatedId`, com `RelatedAccountAmount` para o valor no destino, o que já cobre
moedas diferentes (`pkg/models/transaction.go`). Actual liga as duas pontas por `transfer_id` e **limpa a categoria**
quando as duas contas estão dentro do orçamento (`server/transactions/transfer.ts`). Sure e Cashew: os READMEs citam
transferências entre contas, sem detalhar a regra.

**Saldo.** ezBookkeeping mantém `balance` em centavos (`int64`) e o atualiza com `balance + delta` na mesma sessão do
lançamento; tem um tipo próprio de lançamento "ajuste de saldo" (`MODIFY_BALANCE`). Actual deriva o saldo somando as
transações e marca as conferidas com o banco (`cleared`, `reconciled`).

**Deduplicação.** Actual faz três passadas (`server/accounts/sync.ts`, `matchTransactions`): 1) ID externo igual na
mesma conta; 2) mesma conta, **mesmo valor**, data a ±7 dias e mesmo favorecido; 3) mesma janela e valor, qualquer
favorecido. Cada transação existente só casa **uma vez** (`hasMatched`), o que resolve o R2. Entre candidatos, ganha
a data mais próxima.

**Regras.** Actual: regra = condições (`and`/`or`) + ações, em estágios `pre` / normal / `post`; dentro de cada
estágio, a ordem é por **especificidade** (`is` vale 10, `oneOf` 9, `isapprox` 5, `contains` 0; regra só de
igualdades vale o dobro), com o id como desempate para a ordem ser estável (`rule-utils.ts`). `isapprox` de valor
aceita ±7,5 % (`shared/rules.ts`); de data, ±2 dias.

**Aprendizado.** Actual olha as **5 últimas** transações do mesmo favorecido; se uma delas acabou de ser editada e uma
categoria aparece **3 ou mais vezes**, cria ou atualiza a regra "favorecido é X → categoria Y"
(`transaction-rules.ts`, `getProbableCategory` / `updateCategoryRules`).

**Contas.** ezBookkeeping separa ativo e passivo pelo tipo: dinheiro, corrente, poupança, investimento, CDB, a
receber e virtual são ativos; cartão e dívida são passivos (`pkg/models/account.go`).

**Recorrência.** Actual tem "pular fim de semana" com escolha de antes ou depois (`shared/schedules.ts`,
`getDateWithSkippedWeekend`). ezBookkeeping gera os agendados por cron (porte P2/P3 do plano de UX).
