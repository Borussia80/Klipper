# 07 — Registro de propriedade intelectual

Registro de **toda fonte consultada**, do que foi observado e de **como**. Serve de prova de que a sala limpa foi
respeitada para Sure e Cashew. Atualizar a cada sessão de observação.

## Sessão 1 — 2026-10-17 (análise e planejamento)

### Sure (AGPL-3.0) — sala limpa

| Fonte | Como | O que foi observado | Código lido? |
|---|---|---|---|
| `github.com/we-promise/sure` | Página do repositório via fetch, com instrução para resumir **só o texto do README** | Funcionalidades, plataformas, legenda do print do painel, licença, aviso de marca "Maybe", ausência de demo pública e de menção a fontes/ícones | **Não** |
| Resultados de busca web | Títulos e resumos de resultados | Que é fork comunitário do Maybe, AGPL-3.0 | **Não** |
| Interface em execução | — | **Não observada** (URL não fornecida) | — |
| Prints | — | **Nenhum** | — |

### Cashew (GPL-3.0) — sala limpa

| Fonte | Como | O que foi observado | Código lido? |
|---|---|---|---|
| `github.com/jameskokoska/Cashew` | Página do repositório via fetch, com instrução para resumir **só o texto do README** | Funcionalidades de orçamento e transação, plataformas, link do PWA, licença, "Material You", ausência de menção a fontes/ícones | **Não** |
| Resultados de busca web (inclui listagem da App Store) | Títulos e resumos | Itens de release recentes, preço | **Não** |
| Interface em execução (`budget-track.web.app`) | — | **Não observada** | — |
| Prints | — | **Nenhum** | — |

Resultados de busca listaram forks do Cashew no GitHub; **nenhum foi aberto**.

### ezBookkeeping (MIT) — leitura permitida

| Fonte | Como | O que foi lido |
|---|---|---|
| `ezbookkeeping.mayswind.net` | Fetch do site | Lista de funcionalidades, formatos de importação |
| README / repositório | Fetch | Licença, stack, estrutura |
| API do GitHub, commit `ff168cf1b2138ee9f42cbe490640fff28ea06892` | `gh api` | `LICENSE`, `package.json`, árvore de arquivos, `src/lib/evaluator.ts`, `src/lib/category.ts`, `src/lib/rule.ts`, `src/core/rule.ts`, `src/core/template.ts`, `src/lib/overview_layout.ts`, `pkg/models/transaction_template.go`, `pkg/models/transaction_category.go`, `pkg/cron/cron_jobs.go`, `pkg/services/transactions.go`, `pkg/converters/ofx/ofx_data.go` (+ listagem do diretório `ofx`) |

Cópias locais ficaram no scratchpad da sessão, fora do repositório. **Nenhum código foi copiado para o Klipper.**

## Ícones e fontes

| App | Ícones | Fontes | Como identificado | Recomendação para o Klipper |
|---|---|---|---|---|
| Klipper (hoje) | Phosphor Icons (MIT) via `@phosphor-icons/vue` | Inter, Space Grotesk (OFL-1.1) via Google Fonts | `package.json`, `nuxt.config.ts` | **Manter.** Já vêm da fonte original com licença compatível |
| ezBookkeeping | Material Design Icons (`@mdi/js`, Apache-2.0), Framework7 Icons (MIT), Line Awesome (MIT / OFL) | Não identificado | `package.json` (MIT, leitura permitida) | Não adotar; Phosphor cobre o necessário |
| Sure | **Não identificado** | **Não identificado** | README não cita | Identificar pela interface se houver sessão de observação. Se for biblioteca aberta, só usar a partir do pacote original — mas não há motivo para trocar Phosphor |
| Cashew | **Não identificado** (README só diz "Material You") | **Não identificado** | README | Idem |

## Garantias desta sessão

- Nenhum arquivo de código, CSS, template ou asset de Sure, Maybe ou Cashew foi aberto.
- Nenhum texto de interface desses apps foi reproduzido — não houve sequer acesso à interface. Todos os textos das
  specs são próprios, em pt-BR.
- Nenhum valor visual (cor, espaçamento, raio) desses apps foi medido; os tokens de `04` são os do próprio Klipper (`tokens.css`).
- Nenhum nome, logo ou marca dos três apps aparece como proposta de UI do Klipper.

## Modelo para próximas sessões

```
### Sessão N — AAAA-MM-DD
| App | Fonte (URL/print) | Largura | Telas | O que foi anotado | Código aberto? |
```
