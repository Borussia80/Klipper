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

- A leitura do código do Sure foi feita pelo **OpenAI Codex**, em sessão própria (informado pelo Roberto).
- Os dois relatórios (`docs/reports/`) ficam **só na pasta local do projeto**, fora do Git (`.git/info/exclude`);
  não sobem para o GitHub. A spec clean-room fica em `docs/specs/` e é a única entrada para quem implementar saldo,
  transferência, split e patrimônio.
- O agente desta sessão **leu os três arquivos depois do commit** das 20:16. Nada nas specs desta pasta veio deles.
- O clone `/tmp/sure` **não foi aberto** por este agente.
- Pela separação de fases que o próprio relatório forense define (§9), este agente passou a estar exposto à
  pesquisa do Sure e **não deve ser o implementador clean-room** de saldo, transferência, split e patrimônio.

## Sessão 2 — 2026-10-17 (hledger, Firefly III, Data Importer)

Leitura de código **autorizada pelo Roberto** para esta investigação, com cópia, adaptação e transcrição proibidas.
Clones `--depth 1` no scratchpad da sessão, fora do repositório. Nada foi executado (sem GHC, PHP ou Composer na
máquina) e nada foi instalado no Klipper.

| Projeto | Commit | Licença confirmada | O que foi lido |
|---|---|---|---|
| hledger (`simonmichael/hledger`) | `aee20abe` | GPL-3.0-or-later (`LICENSE`, `package.yaml`) | Balanceamento, inferência de valor, asserções, `.latest`, import, manual (`hledger.m4.md`), testes de `Balancing.hs` e `hledger/test/import` |
| Firefly III | `b9c31006` | AGPL-3.0 (`LICENSE`) | Motor de regras, listeners de criação/edição, ações, recorrências, orçamento automático, conciliação, criação de journal e hash de duplicata, inventário de `tests/` |
| Firefly III Data Importer | `9398df76` | AGPL-3.0 (`LICENSE`) | Envio pela API, métodos de duplicata, remoção de linhas iguais, CAMT, configuração, `AmountTest`, `ConfigurationTest` |

Dossiês (Documentos A–D) em `docs/reports/2026-10-17_{A,B,C,D}_*.md`, **só locais**, fora do Git. Protótipo
independente dos casos-limite (Ruby, dados sintéticos) no scratchpad da sessão; não é código do Klipper.

**Não investigado:** lotes e custo de base do hledger; webhooks, metas (piggy banks), contas a pagar e câmbio do
Firefly; provedores bancários do Data Importer; fluxo CAMT até o envio. **Depende de validação futura:** todo
comportamento do Firefly e do Data Importer (sem teste nos próprios projetos e sem execução aqui) e o uso do hledger
como oráculo (exige instalá-lo em ambiente isolado).

**Exposição:** esta sessão leu código GPL/AGPL; ver a tabela "Quem implementa" no `05-plano-implementacao.md`.

## Sessão 3 — 2026-10-20 a 2026-10-25 (implementação do alfa D1–D3)

Proveniência do código do alfa (saldo derivado, transferência em duas pontas, exclusão restaurável), commitado em
`1bbf81e` e ajustado em `8cd999f` no branch `codex/alpha-financial-core`. Apurada em 2026-10-25 pelos registros de
sessão do Codex (`~/.codex/sessions`), examinando **só os comandos** executados, não as saídas, para não trazer
material restrito para a sessão que apurou.

**Autor.** Sessão do Codex Desktop `01a15560-3e0b-76c1-ab57-4d9fd5400a77`, aberta em 2026-10-19 15:15 (-03). Era a
sessão da pesquisa de UX (`docs/ux-research/09-observacao-ao-vivo.md` e `relatorios/`). Criou em 2026-10-20, entre
17:58 e 18:05, `TransferService`, `AccountBalanceHistory`, `TransfersController`, a migration `20261020010000`,
`useTransfers`, os testes correspondentes e `docs/alpha/01-operacao-segura.md`.

| Material | Lido antes de escrever o código? | Como |
|---|---|---|
| `docs/reports/` (relatórios forense e técnicos) | **Não** | nenhum comando o referencia |
| Código do Sure (`/tmp/sure` ou outro clone) | **Não** | só baixou `compose.example.yml` e usou o app em execução (caixa-preta) |
| Código do hledger, Firefly III e Data Importer | **Não** | Firefly III só pela demonstração pública, no navegador |
| Código do ezBookkeeping (MIT) | **Sim** | clone `--depth 1` em `~/AgentSandbox`; buscas em `pkg/models` e `pkg/core`, inclusive o enum de tipos de lançamento (transferência) e fuso horário |
| Código do Actual (MIT) | **Sim** | clone `--depth 1`; contrato de importação |
| Configuração do Ghostfolio (AGPL-3.0) | **Sim** | busca de variáveis `REDIS_` no container, para executá-lo |
| `05-plano-implementacao.md` e `12-protocolo-de-proveniencia-e-clean-room.md` | Sim | a sessão conhecia a regra de quem implementa |

**Conclusão.** A regra da tabela "Quem implementa" para D2/D3 (não ler o código de Sure ou hledger nem
`docs/reports/`) **não foi violada**, segundo o exame dos comandos. Não é, porém, um clean room formal no
sentido do item 5 do protocolo: a sessão não era um contexto novo que recebeu só a especificação, e tinha lido
código MIT (ezBookkeeping, Actual). Não há indício de cópia; licença MIT exige atribuição só em reuso literal. A
leitura do Ghostfolio não toca D2/D3; vale o limite já registrado no protocolo.

**Continuação em 2026-10-25.** Uma sessão do Claude Code commitou o alfa (`1bbf81e`, `8cd999f`) e fez, com parte
delegada a subagentes Codex, só estas mudanças sobre o código da sessão `01a15560`: edição de uma ponta de
transferência altera as duas; a edição preserva o `kind`; "Desfazer" da exclusão; recusa de transferência de uma
ponta só no endpoint comum; trava do lançamento conciliado (C-9, L-22). Nenhum deles abriu `docs/reports/`, `*.zip` de pesquisa ou clones
de terceiros; os briefs proibiam. A sessão do Claude leu trechos de `03-specs/02` e `03`, do plano e de
`implementation-traceability.md`, e recebeu um panorama dos estudos feito só sobre documentos liberados.

**Limite.** O exame cobriu os comandos registrados, não as saídas; não permite confirmar leituras feitas por outros
meios, como navegador ou ferramentas sem comando registrado.
