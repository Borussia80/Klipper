# 06 — Plano de implementação

**Aprovado em 2026-10-17.** Direção visual náutica, sem mudança de paleta; cores de banco mantidas; "+" no centro da
barra inferior mobile; dia de fechamento e de vencimento do cartão incluídos.

Regras do projeto valem em tudo: teste antes do código (Vitest / RSpec); um PR por fatia; merge um por vez esperando
o CI do `main`; uso local primeiro (Rails 3000, Nuxt 3001; Render/Vercel hibernados); Postgres de teste via
`podman start klipper-pg-test`.

## Escopo liberado agora: Fase 0 + Fatias 1 e 2

**Fatias 3–7 estão bloqueadas** até a análise de domínio (`docs/domain-research/`) ser aprovada — evita retrabalho em
saldo, cartão e agendados.

---

## Plano de execução — jornadas do alfa

Este plano detalha as Fatias 2–4 para o alfa manual. Não altera as dependências ou os bloqueios registrados abaixo: a liberação de cada fatia e de suas regras financeiras deve ser verificada contra o plano de domínio vigente. O estado de cada item deve ser confirmado no código e no CI antes de ser marcado como concluído.

### 0. Referência e preparação

- [ ] Executar RSpec, Vitest e typecheck; registrar falhas preexistentes.
- [ ] Com dados fictícios, percorrer contas, receita, despesa, transferência, exclusão e restauração; registrar resultados em desktop, 390 px e teclado.
- [ ] Confirmar os contratos atuais de saldo, histórico, transações e relatórios.

### 1. Navegação e lançamento — Fatia 2

- [ ] Incluir “+” central na navegação mobile; mover Investimentos para Mais e abrir lançamento rápido com foco no valor.
- [ ] Reutilizar formulário e componentes existentes; oferecer entrada/saída, conta e data padrão editáveis e categoria opcional.
- [ ] Validar valor; preservar rascunho em erro; confirmar descarte quando alterado; oferecer confirmação e desfazer após salvar.
- [ ] Preservar acesso e atalhos no desktop. Avaliador de expressões pode ser entregue em PR separado, seguindo a spec 02 e a política de terceiros do plano de domínio.
- **Aceite:** despesa com padrões em até quatro toques após o “+” (digitação como sequência); 390 px sem rolagem horizontal; desfazer recompõe saldo; fluxo completo por teclado.

### 2. Movimento — Fatia 4

- [ ] Acrescentar busca e filtros por período, tipo, conta, categoria e portador; preservar consulta ao editar e retornar.
- [ ] Exibir filtros ativos, ação de limpar e lista mobile legível, além de estados de carregamento, vazio, erro e nova tentativa.
- [ ] Entregar edição em lote em incremento próprio se necessário: operação transacional, escopada por usuário, sem alteração parcial.
- **Aceite:** filtro de categoria pai inclui filhas; contexto sobrevive à edição; IDs de outro usuário são rejeitados sem alterações; exclusão/restauração de transferência mantém as duas pontas; teclado acessa todas as ações.

### 3. Detalhe de conta — Fatia 4, dependente de D1/D2

- [ ] Criar detalhe com saldo, saldo inicial datado e movimentos, reutilizando a lista de Movimento.
- [ ] Usar o contrato real do histórico e as regras do domínio; identificar transferências e preservar contexto ao voltar.
- [ ] Tratar ausência de movimentos, histórico insuficiente, carregamento e erro isolado.
- **Aceite:** abertura R$ 1.000 + receita R$ 500 − despesa R$ 200 resulta em R$ 1.300; transferência aparece nas duas contas; datas anteriores à abertura são “sem dado”; falha no histórico não oculta os demais dados.
- Cartões, fechamento e vencimento dependem de D4; não bloqueiam o detalhe das contas do alfa manual.

### 4. Painel — Fatia 3, conforme dependências de domínio

- [ ] Destacar patrimônio ou saldo consolidado conforme dados e definições suportados; mostrar resultado mensal e últimos movimentos.
- [ ] Incluir alertas acionáveis apenas quando fundamentados em dados disponíveis; isolar carregamento e falha por bloco.
- [ ] Mostrar evolução somente com histórico suficiente; oferecer estados vazios e recuperação.
- **Aceite:** valores coincidem com contas e relatórios; conta negativa gera alerta que desaparece ao corrigir; não há gráfico fictício; 390 px sem rolagem horizontal; falha de uma fonte não derruba outros blocos.
- Alertas de fatura e ritmo avançado dependem das regras correspondentes; não simular dados.

### 5. Validação integrada e liberação

- [ ] Criar duas contas fictícias; registrar receita, despesa e transferência; filtrar e editar; conferir saldos e histórico; excluir/restaurar transferência e comparar o painel com os relatórios.
- [ ] Repetir em desktop, 390 px e somente com teclado.
- [ ] Executar os requisitos de operação segura, exportação e restauração de backup em [operação segura do alfa](../alpha/01-operacao-segura.md) antes de receber dados pessoais.

Cada incremento segue teste antes de código, PR por fatia, revisão e CI verde. Registrar evidência e data dos critérios satisfeitos; não confundir plano com implementação concluída.

---

## Fase 0 — Correções

### 0.1 Isolar a suíte do Vitest da API local
`vitest.config.ts` aponta `NUXT_PUBLIC_API_URL` para uma porta morta. PR #135.

### 0.2 Documentos
Esta pesquisa e os docs de design alinhados à direção náutica.

### 0.3 `pages/configuracoes.vue` + teste de tokens
- Trocar os tokens inexistentes (`--ink`, `--ink-3`, `--rule`, `--space-3/4/5`) pelos reais.
- Teste (`assets/css/__tests__/tokens.test.ts`) que lê todo `var(--x…)` de `pages/`, `components/`, `layouts/` e
  CSS e falha se `--x` não estiver definido:
  - definidos = `--x:` em `tokens.css`, `main.css` e nos `<style>` dos `.vue` (variável escopada);
  - `var(--x, fallback)`: conta o nome; o fallback é ignorado, ou conferido se também for `var`;
  - variável definida inline (`style="--x:…"`, `:style="{ '--x': … }"`) conta como definida;
  - `--bank-*` aceito por prefixo (hoje definidos em `tokens.css` e não usados por nenhuma tela — `BankIcon` tira a
    cor de `@edusites/bancos-brasil`; dead code pré-existente, só registrado);
  - **lista de exceções explícita no próprio teste**, cada uma com o porquê; exceção que deixou de ser usada também
    falha.

### 0.4 `orcamento.vue` — `budgetSpentRatio(...) ?? 0`
"Sem orçamento" vira "0 %". Corrigido na Fatia 5, junto com a tela.

## Fatia 1 — Categorias em dois níveis (spec 07)

Backend primeiro. Usa `categories.active` como "oculta" (já existe). Migração `parent_id`, `position`,
`merged_into_id`. Validações, `CategoryMergeService` e a regra de orçamento pai × filha estão detalhados em
`05-specs/07-categorias.md`. Frontend: `composables/useCategoryTree.ts` (porte P4), seletor reutilizável e gestão em
`/configuracoes`.

## Fatia 2 — Lançamento rápido + navegação mobile (spec 02)

- `utils/amountExpression.ts` (porte P1), regras de ponto × vírgula e casos de teste em `05-specs/02-lancamento-rapido.md`.
- Reaproveitar `composables/useLancamentoForm.ts`; a folha mobile é apresentação nova.
- `MobileNav.vue`: Painel · Movimento · [+] · Orçamento · Mais (Investimentos para "Mais").
- `GET /categories?sort=usage&limit=8` e `GET /categories/suggest?description=` (usa `AutoCategorizerService.call`).
- Toast com "Desfazer" via `useToast`.
- Cria `THIRD_PARTY_NOTICES.md` na raiz.

---

## ⛔ Bloqueadas até `docs/domain-research/` ser aprovada

| Fatia | Spec | Já decidido para quando liberar |
|---|---|---|
| 3 — Painel com patrimônio + alarmes | 01 | Migrar `dia_fechamento` **junto** com `dia_vencimento`. Dia maior que o mês → último dia; vencimento em fim de semana/feriado → próximo dia útil; fechamento não se desloca. Testes: fevereiro bissexto e não, 30/31, sábado, domingo, feriado |
| 4 — Transações e contas | 03, 04 | `bulk_update` numa transação de banco, com escopo por usuário (ids ou categoria de outro usuário → 404, nada alterado). *O item chegou cortado em "escopo por" — confirmar ao liberar* |
| 5 — Orçamento | 05 | Ritmo, por dia, `copy_previous`, correção 0.4 |
| 6 — Agendados | 06 | Portes P2/P3 sem job; conciliação sugerida primeiro; o merge de categorias passa a mover agendados |
| 7 — OFX + regras | — | Portes P5/P6 |

---

## Itens do ezBookkeeping a portar

| # | Origem (commit `ff168cf`) | O que faz | Destino no Klipper | Fatia |
|---|---|---|---|---|
| P1 | `src/lib/evaluator.ts` | Avalia `45,90+12` sem `eval`, com limites | `apps/klipper-web/utils/amountExpression.ts` | 2 |
| P2 | `pkg/models/transaction_template.go` + `src/core/template.ts` | Modelo de frequência | `scheduled_transactions` + enum no model | 6 |
| P3 | `pkg/services/transactions.go#CreateScheduledTransactions` | Quais agendamentos vencem num intervalo | `app/services/scheduled_occurrences_calculator.rb` | 6 |
| P4 | `pkg/models/transaction_category.go` + `src/lib/category.ts` | Categoria com pai e ordem; marcar pai marca filhas | migração + `composables/useCategoryTree.ts` | 1 |
| P5 | `src/core/rule.ts` + `src/lib/rule.ts` | Regras condição → ação na importação | `app/services/import_rules/` (desenho) | 7 |
| P6 | `pkg/converters/ofx/*` | Leitura de OFX/QFX | `app/services/bank_import/ofx_reader.rb` | 7 |
| P7 | `src/lib/overview_layout.ts` | Blocos do painel configuráveis | **Não portar** | — |

Cabeçalho obrigatório em cada arquivo portado, e entrada com a licença MIT integral em `THIRD_PARTY_NOTICES.md`:

```
Portions adapted from ezBookkeeping (https://github.com/mayswind/ezbookkeeping), commit ff168cf,
<arquivo de origem>. Copyright (c) 2020-2026 MaysWind. Licensed under the MIT License.
```

## Riscos

| Risco | Mitigação |
|---|---|
| Telas sem moldura ou sem hierarquia | Critério de aceite com screenshot em 1440 px e 390 px em toda spec |
| Contaminação da sala limpa durante a implementação | Specs autossuficientes; `07-registro-pi.md` atualizado a cada consulta |
| Soma por pai errada muda relatórios | Specs dos calculators com pai + filhas antes de mudar o código |
| Render Free hiberna | Agendados sem job; cálculo sob demanda |

## Verificação de cada PR

1. `cd apps/klipper-web && npm run test` verde.
2. `podman start klipper-pg-test` e `bundle exec rspec` verde.
3. App local nas duas larguras, critérios de aceite da spec conferidos, screenshot no PR.
4. CI verde → merge → CI do `main` verde → próximo PR.

