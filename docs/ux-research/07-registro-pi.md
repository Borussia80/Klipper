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

## Sessão 2 — 2026-10-19 (observação ao vivo)

| App | Fonte/ambiente | Telas observadas | Código aberto? |
|---|---|---|---|
| Sure | imagem oficial em container local isolado | cadastro, onboarding, painel vazio, tentativa de conta manual sintética, movimentos vazios/filtros e configuração/validação de orçamento | **Não** |
| Cashew | PWA oficial em execução | início vazio desktop, lançamento sintético, edição, filtros, confirmação de cancelamento e formulário em 390 px | **Não** |
| ezBookkeeping | imagem oficial em container local isolado | login, cadastro, preferências, conta local sintética, categorias pai/filha, lista, busca e assistente de importação | **Não** |
| Firefly III | demonstração pública oficial em execução | painel preenchido, orçamento, detalhe de conta e largura de 390 px | **Não** |
| Actual Budget | demonstração pública oficial em execução, sem sincronização | orçamento preenchido, histórico de conta, estados de agendamento e largura de 390 px | **Não** |
| Wealthfolio (AGPL-3.0) | binário oficial em servidor local isolado | onboarding, criação de conta, fotografia de saldo, detalhe/histórico de snapshots e painel preenchido | **Não** |
| Ghostfolio (AGPL-3.0) | páginas públicas oficiais e imagem oficial em ambiente local isolado | escopo de patrimônio, criação de administrador local, token de recuperação, onboarding, contas e falha de dependência local | **Sim — somente configuração de ambiente distribuída, para ligar o Redis local** |

## Sessão 3 — 2026-10-20 (Lote 0: importação)

| App | Fonte/ambiente | Evidência e escopo | Código aberto? |
|---|---|---|---|
| ezBookkeeping | container local e API local do produto | CSV sintético, mapeamento, três falhas recuperáveis, conclusão 13/13 e reimportação 13/13; fonte MIT no commit `3dcc316e1fb6a190d6a0dd13fbe4052d17b9315c` | **Sim — somente para critério técnico de repetição de envio** |
| Actual Budget | demonstração pública oficial | conta aberta e fluxo de importação iniciado; sandbox não entregou o arquivo ao seletor oculto, portanto nenhuma alteração foi concluída | **Sim — somente contrato técnico de identificador externo de importação no commit `8fba0e87cf7a4cda6ab5ea8012477bd7051f6ebc`** |

Nenhum código, texto de interface, schema ou asset dessas referências foi copiado para o Klipper. As regras nos relatórios são descritas em linguagem funcional própria.

As observações de comportamento desta sessão estão em `09-observacao-ao-vivo.md`. Nenhum código, stylesheet, template, asset ou texto de interface foi copiado para o Klipper. O Wealthfolio foi executado apenas como binário distribuído oficialmente; seu código não foi aberto. No Ghostfolio, a inspeção limitada de configuração confirmou a variável de conexão de cache necessária para o ambiente local; nenhuma implementação do Klipper foi derivada por cópia.

## Autorização de estudo de software livre — 2026-10-20

O usuário autorizou expressamente leitura, inspeção e estudo de código sob GPL/AGPL e outras licenças livres. A partir desta data, referências podem incluir comportamento executável e análise técnica, desde que cada achado registre origem e licença quando relevante.

Essa autorização **não** transforma automaticamente a análise em *clean room*. Uma fonte cujo código seja lido passa a ser classificada como técnica/"dirty" para aquela linha de trabalho. O Ghostfolio, nesta sessão, tem essa classificação limitada: a configuração de ambiente foi lida; portanto, este contexto não deve implementar uma reconstituição *clean room* derivada da análise técnica dele.

Nenhuma cópia de código copyleft entrará no repositório sem revisão explícita de compatibilidade, atribuição e obrigações de distribuição. A implementação preferida continua sendo autoral, baseada em requisito funcional; o processo formal fica definido em `12-protocolo-de-proveniencia-e-clean-room.md`.

## Modelo para próximas sessões

```
### Sessão N — AAAA-MM-DD
| App | Fonte (URL/print) | Largura | Telas | O que foi anotado | Código aberto? |
```
