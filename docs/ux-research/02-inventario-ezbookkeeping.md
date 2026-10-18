# 02 — Inventário: ezBookkeeping

**Licença:** MIT — `Copyright (c) 2020-2026 MaysWind (i@mayswind.net)`. Código **pode** ser lido e portado com
atribuição.
**Versão estudada:** branch `main`, commit `ff168cf1b2138ee9f42cbe490640fff28ea06892` (consultado em 2026-10-17
via API do GitHub).
**Papel no Klipper:** estrutura e funcionalidade — categorias em dois níveis, transações agendadas, importação,
configurações, separação desktop/mobile.

## Estado da observação

| Fonte | Situação |
|---|---|
| Instância em execução (`[URL_EZBOOKKEEPING]`) | **Não observada** (placeholder). Comportamento abaixo vem do código, não da tela |
| Prints (`prints/ezbookkeeping/`) | **Não existem** |
| Documentação pública | Site `ezbookkeeping.mayswind.net` e README |
| Código-fonte (MIT) | Lidos arquivos específicos, listados em `07-registro-pi.md` |

## Stack (de `package.json`)

| Camada | Biblioteca | Observação para o Klipper |
|---|---|---|
| UI desktop | **Vuetify 4** | Klipper não usa biblioteca de componentes — não importar |
| UI mobile | **Framework7 9** (+ framework7-vue) | Idem. Interessa o *padrão* de ter duas árvores de view, não a lib |
| Ícones | `@mdi/js` (Material Design Icons, Apache-2.0), `framework7-icons` (MIT), `line-awesome` (MIT/OFL) | Klipper já usa Phosphor (MIT); não trocar |
| Gráficos | ECharts 6 + vue-echarts | Avaliar só se os gráficos próprios do Klipper não derem conta do saldo por conta |
| Números | `decimal.js` | O Klipper já trata dinheiro como decimal no Rails |
| Backend | Go | Lógica portável para Ruby, não código |

## Separação desktop/mobile

`src/views/desktop/` e `src/views/mobile/` são **duas árvores de telas completas**, com o mesmo núcleo
(`src/core`, `src/lib`, `src/stores`) por baixo. Telas em ambas: contas, categorias, transações, estatísticas,
templates (agendadas), tags, câmbio, configurações, visão geral. Só desktop: `insights`, `customicons`, `users`.

**Para o Klipper:** não duplicar páginas. O Klipper tem 13 rotas e um único dev; duas árvores dobrariam a
manutenção. O que vale levar é a **regra**: lógica em composables, e componentes de apresentação distintos só onde
a interação difere de fato (lançamento rápido, lista com gestos). Ver `03-matriz-referencias.md`.

## Funcionalidades relevantes, pelo código

### E1 — Categorias em dois níveis
- `pkg/models/transaction_category.go`: categoria com `Type` (receita/despesa/transferência), `ParentCategoryId`
  (0 = raiz), `DisplayOrder`, `Hidden`, ícone e cor. Índice composto por usuário + tipo + pai + ordem.
- `src/lib/category.ts`: criação a partir de **presets localizados com subcategorias**; funções para seleção em
  árvore (marcar pai marca filhos, "todas marcadas?"), usadas nos filtros.
- Dois níveis **fixos** — não é árvore arbitrária. Bom: evita recursão e mantém a UI simples.

### E2 — Transações agendadas (templates)
- `pkg/models/transaction_template.go`: um template é `NORMAL` (atalho de lançamento) ou `SCHEDULE` (agendado).
  Frequência: desativada, diária, semanal, mensal, anual, a cada N dias; campo `ScheduledFrequency` guarda os dias
  (ex.: "1,15" no mensal); `ScheduledStartTime`/`ScheduledEndTime` opcionais; `ScheduledAt` = minuto do dia.
- `pkg/cron/cron_jobs.go` + `pkg/services/transactions.go#CreateScheduledTransactions`: job a cada 15 min busca
  templates cuja janela de horário cai no intervalo e que estão dentro de início/fim, e **cria a transação
  automaticamente**.
- `src/core/template.ts`: enum de frequência no frontend.

### E3 — Regras de substituição na importação
- `src/core/rule.ts` + `src/lib/rule.ts`: regra = condições (campo + operador) → ações.
  - Campos: categoria, conta origem/destino, tag, valor, descrição (exata, sem caixa, normalizada).
  - Operadores: é/vazio/não vazio, igual, contém, começa/termina com, regex, maior/menor, entre.
  - Ações: definir tipo, categoria, conta, valor, fuso; adicionar/substituir/remover tag.
- Aplicada na **prévia** da importação, antes de gravar.

### E4 — Importação de muitos formatos
- `pkg/converters/`: CSV, Excel, OFX/QFX, QIF, IIF, Camt.052/053, MT940, GnuCash, Firefly III, Beancount e formatos
  chineses (Alipay, WeChat, JD). O **OFX** é o que interessa ao Brasil: Itaú, Nubank, BB, Bradesco e Inter exportam.
- Para o Klipper: `ofx_data.go` + `ofx_data_reader.go` + `ofx_transaction_data_file_importer.go` são a referência
  para um adapter OFX genérico — alinhado à decisão "importação padronizada, não por banco".

### E5 — Avaliador de expressão no campo de valor
- `src/lib/evaluator.ts`: o usuário digita `45,90+12` e o campo calcula. Converte para pós-fixa com prioridade de
  operadores, valida limites mínimo/máximo, sem `eval`. ~220 linhas autocontidas.

### E6 — Visão geral com layout configurável
- `src/lib/overview_layout.ts` + `src/consts/overview_layout.ts`: blocos do painel com ordem e visibilidade
  escolhidas pelo usuário. Para o Klipper, **baixa prioridade**: layout estável e previsível lê melhor;
  no máximo ocultar blocos.

### E7 — Configurações
- Árvore `settings/` separa: conta do usuário, segurança (2FA, sessões), preferências de exibição (formato de data e
  número, primeiro dia da semana, início do ano fiscal — `src/core/fiscalyear.ts`), dados (exportar, limpar).
- Para o Klipper: **a organização em seções** é a referência; 2FA/OIDC ficam fora.

## Estados (pelo código, a confirmar na tela)
- Carregamento com esqueleto (`skeleton-elements`).
- Tradução completa via `vue-i18n` — todo texto é chave; o Klipper fica só em pt-BR, sem i18n.
