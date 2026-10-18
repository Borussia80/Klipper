# 06 — Registro de propriedade intelectual

Toda fonte consultada nesta análise, o que se observou e como. Complementa `docs/ux-research/07-registro-pi.md`.

## Sessão 1 — 2026-10-17

### Sure / Maybe Finance (AGPL-3.0) — sala limpa

| Fonte | Como | O que foi observado | Código lido? |
|---|---|---|---|
| — | — | Nada novo nesta sessão. A URL da interface (`[URL_SURE]`) veio sem preencher no pedido | **Não** |

### Cashew (GPL-3.0) — sala limpa

| Fonte | Como | O que foi observado | Código lido? |
|---|---|---|---|
| `budget-track.web.app` | — | **Não aberto** nesta sessão | **Não** |

Nenhuma regra das specs foi tirada do Sure ou do Cashew. Onde as specs comparam, dizem "não observado".

### Actual Budget (MIT, "Copyright James Long") — leitura permitida

| Fonte | Como | O que foi lido |
|---|---|---|
| `github.com/actualbudget/actual`, commit `bde50c3` | `git clone --depth 1 --sparse` no scratchpad da sessão, fora do repositório | `LICENSE.txt`; `packages/loot-core/src/server/accounts/sync.ts` (`matchTransactions`, `compareFuzzyMatchCandidates`); `server/rules/rule.ts`, `condition.ts` (operadores, `isapprox`), `rule-utils.ts` (`computeScore`, `rankRules`); `server/transactions/transaction-rules.ts` (`getProbableCategory`, `updateCategoryRules`); `server/transactions/transfer.ts`; `shared/rules.ts` (`getApproxNumberThreshold`); `shared/schedules.ts` (lista de funções, `getDateWithSkippedWeekend`) |

### ezBookkeeping (MIT, "Copyright (c) 2020-2026 MaysWind") — leitura permitida

| Fonte | Como | O que foi lido |
|---|---|---|
| `raw.githubusercontent.com/mayswind/ezbookkeeping/ff168cf/…` | `curl` para o scratchpad | `pkg/models/transaction.go` (tipos, `RelatedId`, `RelatedAccountAmount`), `pkg/models/account.go` (categorias de conta, ativo/passivo), `pkg/services/transactions.go` (atualização de saldo por delta) |
| Arquivos da sessão de UX | Já registrados em `docs/ux-research/07-registro-pi.md` | — |

A URL da interface (`[URL_EZBOOKKEEPING]`) veio sem preencher. Não houve observação em execução.

### Fontes públicas (conhecimento financeiro e normativo)

| Assunto | Fonte |
|---|---|
| Arredondamento meio-par | ABNT NBR 5891 |
| Feriados nacionais | Lei 662/1949 e alterações; Lei 14.759/2023 (20 de novembro) |
| Páscoa | Algoritmo de Meeus/Jones/Butcher (domínio público) |
| PTAX | Banco Central, API Olinda (dados abertos) |
| CDI e IPCA | Banco Central, SGS séries 12 e 433 |
| Rotativo do cartão | Resolução CMN 4.549/2017; Lei 14.690/2023 (teto de 100 %) |
| Liquidação antecipada | Código de Defesa do Consumidor, art. 52, §2º |
| IOF | Decreto 6.306/2007 e alterações (alíquota varia; por isso a tabela com vigência) |
| Tabela Price, Dietz modificado, TWR, TIR, valor presente | Matemática financeira, domínio público |

## Garantias

- Nenhum arquivo de código do Sure, do Maybe ou do Cashew foi aberto, nem nesta sessão nem na de UX.
- Do Actual e do ezBookkeeping, nada foi copiado para o repositório. As specs descrevem os algoritmos com palavras
  próprias, e os itens a portar estão listados com origem e destino em `05-plano-implementacao.md`.
- As cópias locais ficaram no scratchpad da sessão, fora do repositório.

## Sessão 1, adendo — 2026-10-17, depois das 20:52

Os documentos desta pasta foram commitados às **20:16** (`git log` do branch `docs/domain-research`). Às 20:52 e
20:56 apareceram no working tree, fora desta pasta e sem commit, três arquivos de outra sessão:
`docs/reports/2026-10-17_sure_forensic_research.md`, `docs/reports/2026-01-17_report_codex_opensource_app.md` e
`docs/specs/klipper_financial_cleanroom_spec_v1.md`. O relatório forense descreve uma leitura do **código-fonte do
Sure** (clone em `/tmp/sure`, revisão `98084bfc`).

- O agente desta sessão **leu os três arquivos depois do commit** das 20:16. Nada nas specs desta pasta veio deles.
- O clone `/tmp/sure` **não foi aberto** por este agente.
- Pela separação de fases que o próprio relatório forense define (§9), este agente passou a estar exposto à
  pesquisa do Sure e **não deve ser o implementador clean-room** de saldo, transferência, split e patrimônio.
