# Roadmap — Klipper Wealth OS

**Gerado em:** 2026-07-06
**Auditado em:** 2026-07-27 — as 6 lacunas abaixo foram confirmadas como implementadas
(schema, serviços, endpoints e UI, todas com teste automatizado associado), via leitura
direta do código em `apps/klipper-api` e `apps/klipper-web`. Este documento passa a
funcionar como registro histórico da decisão de produto + mapa de onde cada peça mora
no código, não mais como lista de pendências.
**Base:** resumo de arquitetura/produto do Klipper (monorepo `apps/klipper-web` + `apps/klipper-api` + `apps/quebec-web`, Nuxt 4 + Rails 8)
**Objetivo deste documento:** fechar as 5 lacunas entre o Klipper atual (orçamento/investimento genérico) e o "wealth OS" real que o uso pessoal do Roberto exige — gestão familiar multi-portador, extrato/fatura em PDF, e priorização de dívida.

Este arquivo deve viver na raiz do repo (ou em `docs/`) e ser referenciado no `CLAUDE.md` do projeto, para que qualquer sessão do Claude Code o leia antes de propor mudanças.

---

## Como usar este roadmap com o Claude Code

O Klipper já passou por 3 reescritas de stack (Streamlit → Next.js → Nuxt/Rails). Isso normalmente não acontece por o Claude Code "não entregar" — acontece quando cada sessão recebe um pedido vago e reinterpreta o problema do zero, sem uma âncora de decisão já tomada. Este roadmap existe para ser essa âncora. Regras de uso:

1. **Uma lacuna por sessão/branch.** Nunca peça "implementa o roadmap inteiro". Cada item abaixo é uma unidade de trabalho fechada, com seu próprio critério de aceite.
2. **Peça um plano antes do código.** Primeiro prompt de cada sessão: *"Antes de escrever código, me mostra o plano: migrations necessárias, endpoints novos/alterados, componentes Vue afetados. Não escreva código ainda."* Só aprove o código depois de revisar esse plano — é o que evita retrabalho tipo as reescritas anteriores.
3. **Aponte para o padrão existente, nunca deixe o Claude Code inventar um novo.** Ex: *"Use o BaseModal e o composable useModal já existentes para este novo modal, não crie um padrão novo."* Mesma lógica para os design tokens (`tokens.css`) e o `JwtService`.
4. **Não toque no legado.** `app.py`, `pages/`, `core/`, `web/` (Streamlit/Next.js) estão marcados para remoção — instrua explicitamente para ignorá-los como referência.
5. **Defina "pronto" com teste, não com "parece que funciona".** Peça que o Claude Code escreva um teste (RSpec no Rails, Vitest no Nuxt) que comprove o critério de aceite antes de considerar o item fechado.
6. **Revise o diff antes de mergear.** Especialmente nos itens 1 e 2 (schema novo) — mudança de modelo de dados é a mais cara de desfazer depois.

Ordem sugerida de execução: **1 → 2 → 3 → 4 → 5** (cada item depende dos dados que o anterior estrutura).

---

## Lacuna 1 — Importação de extrato/fatura em PDF (não só CSV)

**Prioridade:** Alta — é a base de tudo, sem isso o resto do roadmap não tem dado real para trabalhar.

**Estado atual: ✅ Implementado.** Backend: `app/services/pdf_import_service.rb` +
`app/services/pdf_adapters/{registry,base_adapter,itau_extrato_adapter,itau_fatura_adapter}.rb`,
`Api::V1::ImportsController#preview`/`#confirm`. Frontend: `pages/importar.vue` +
`composables/useImport.ts` (`previewFile`/`confirmImport`) — aceita CSV e PDF, com tela
de preview antes de confirmar.

**Necessidade real:** ler PDF de extrato de conta-corrente (Itaú) e fatura de cartão (Itaú Personnalité, Santander, Nubank), cada um com layout diferente.

**Critério de aceite:**
- Upload de PDF → extração de linhas (data, descrição, valor, saldo quando houver) → tela de preview antes de confirmar import (igual ao fluxo de CSV já existente)
- Suporta pelo menos 2 layouts de origem distintos (extrato de conta Itaú + fatura de cartão Itaú) via um padrão de "adapter por instituição" — não um parser único genérico, porque cada banco formata diferente
- Falha de parsing mostra erro claro (linha/página) em vez de importar dado incorreto silenciosamente

**Nota técnica:** cada instituição financeira precisa de um adapter próprio (`ItauExtratoAdapter`, `ItauFaturaAdapter`, `SantanderFaturaAdapter`, `NubankFaturaAdapter`). Resista à tentação de um parser universal — a experiência de campo (esta análise manual) mostrou que os leiautes variam bastante mesmo dentro do mesmo banco (extrato de conta ≠ fatura de cartão).

---

## Lacuna 1.5 — Deduplicação de importação

**Prioridade:** Alta — bloqueia confiar o uso real no Klipper assim que a Lacuna 1 estiver no ar.

**Estado atual: ✅ Implementado.** Migration
`db/migrate/20260707120000_add_dedupe_hash_to_transactions.rb`, cálculo em
`app/services/bank_import/dedupe_hash.rb` (SHA256 de user/conta/data/descrição/valor/tipo),
rejeição em `app/services/bank_import/transaction_writer.rb`. Frontend: tela de resultado
mostra `result.duplicates` ("X duplicata(s) ignorada(s)") em `pages/importar.vue`.

**Necessidade real:** a primeira vez que um extrato/fatura com período sobreposto ao de uma
importação anterior for reimportado, o sistema vai duplicar transação sem esse mecanismo.

**Critério de aceite:**
- Hash único por transação (`data + descrição + valor + conta`) calculado no momento da
  persistência (CSV e PDF)
- `confirm` (Lacuna 1) e o import de CSV rejeitam/ignoram duplicata exata em vez de criar uma
  nova transação silenciosamente
- Não precisa ser sofisticado (sem UI de "revisar duplicatas" nesta fase) — só não duplicar

**Nota técnica:** provável coluna `dedup_hash` (ou índice único calculado) em `transactions`;
verificar antes de criar cada transação nova, tanto no fluxo de CSV quanto no `confirm` do PDF.

---

## Lacuna 2 — Portador (quem gastou) no modelo de dados

**Prioridade:** Alta.

**Estado atual: ✅ Implementado.** Backend: model `app/models/member.rb`, migrations
`create_members`/`add_member_to_transactions` (FK opcional em `transactions`),
`Api::V1::MembersController`, matching automático em `app/services/bank_import/member_matcher.rb`.
Frontend: `pages/portadores.vue` + `ModalNovoMembro.vue`, filtro por portador em
`pages/dashboard.vue` e `pages/relatorios.vue`.

**Necessidade real:** cada lançamento (principalmente os de cartão) precisa carregar um portador.

**Critério de aceite:**
- Nova entidade `portador` (ou `membro_familia`): nome, relação (titular/dependente)
- Cada `transacao` ganha uma FK opcional para `portador` (opcional porque nem toda transação tem portador definido, ex: PIX de conta corrente)
- Import de fatura de cartão (Lacuna 1) já popula o portador automaticamente quando o PDF identifica o nome do titular do cartão (a maioria das faturas já traz isso por seção)
- Relatórios e dashboard podem filtrar por portador

---

## Lacuna 3 — Classificação Fixo × Cartão/Parcelamento × Variável, e Rotineiro × Pontual

**Prioridade:** Média-alta.

**Estado atual: ✅ Implementado.** Backend: migration `add_natureza_to_categories`, enum em
`app/models/category.rb`, cálculo de recorrência em
`app/services/category_recurrence_calculator.rb`, endpoint `natureza_split`. Frontend:
select de natureza em `ModalNovaCategoria.vue`, exibição ("presente em X dos últimos Y
meses") em `BudgetCategoryCard.vue`, gráfico donut fixo × cartão × variável no dashboard.

**Necessidade real:** replicar a lógica validada manualmente nesta análise — separar o que é compromisso fixo (pensão, aluguel, terapia, contas) do que é cartão/parcelamento (alavanca real de ajuste) e do que é variável; e separar o que é rotineiro (aparece na maioria dos meses) do que é pontual (evento isolado, tipo viagem ou quitação de financiamento).

**Critério de aceite:**
- Campo `natureza` na categoria: `fixo` / `cartao_parcelamento` / `variavel`
- Campo calculado `recorrencia` por categoria/lançamento recorrente: `rotineiro` (presente em ≥60% dos últimos N meses) / `ocasional` (30-60%) / `pontual` (<30%) — mesmo critério usado manualmente nesta análise
- Dashboard mostra o split fixo × cartão × variável (equivalente ao gráfico de pizza que já fizemos na planilha)
- Tela de categoria mostra "presente em X dos últimos Y meses" para o usuário decidir se algo é rotina ou não

---

## Lacuna 4 — Reembolso de convênio vinculado ao gasto de terapia

**Prioridade:** Média.

**Estado atual: ✅ Implementado.** Backend: FK `reimbursed_by_category_id` (self-referencing
em `Category`, migration `add_reimbursed_by_category_to_categories`),
`app/services/reimbursement_coverage_calculator.rb`, endpoint `reimbursement_coverage`.
Frontend: `ModalEditarReembolso.vue` (vínculo despesa↔receita), colunas de % de cobertura
em `pages/orcamento.vue`.

**Necessidade real:** vincular lançamentos de despesa (ex: pagamento a terapeuta) a lançamentos de receita (reembolso do convênio), calculando % de cobertura ao longo do tempo — hoje isso só existe porque foi calculado manualmente na planilha.

**Critério de aceite:**
- Tag/vínculo entre uma categoria de despesa (ex: "Terapia Pedro") e uma categoria de receita (ex: "Reembolso Bradesco")
- Card ou tela mostrando: gasto no período, reembolsado no período, % de cobertura, e alerta visual se a cobertura cair muito abaixo da média histórica

---

## Lacuna 5 — Comparador de custo de dívida entre cartões (priorização de quitação)

**Prioridade:** Baixa-média (evento infrequente, mas de alto impacto quando ocorre — como visto nesta análise com a fatura Itaú Personnalité).

**Estado atual: ✅ Implementado.** Backend: migration `add_debt_fields_to_accounts` (saldo
de fatura, pagamento mínimo, juros rotativo a.m./a.a., IOF projetado em `Account`),
`app/services/debt_ranking_calculator.rb`, endpoint `debt_ranking`. Frontend:
`DebtRankingCard.vue` em `pages/contas.vue`, com simulação "pagando só o mínimo".

**Necessidade real:** dado o saldo em aberto e a taxa de juros do rotativo/parcelamento de cada cartão, ranquear qual quitar primeiro.

**Critério de aceite:**
- Campos por cartão: `saldo_fatura_atual`, `juros_rotativo_am`, `juros_rotativo_aa` (dado que já vem estampado na própria fatura, útil capturar no import da Lacuna 1)
- Tela (ou seção em `/contas`) que ranqueia os cartões por custo do rotativo, do mais caro para o mais barato
- Simulação simples: "se pagar só o mínimo por 1 mês, o saldo sobe para X" — replicando o cálculo que fizemos manualmente para a fatura Itaú

---

## Bugs conhecidos (achados em auditoria, não silenciar)

### `investimentos.vue` — header com valores hardcoded, não calculados

**Estado atual: ✅ Resolvido.** Commit `905d8f1` (2026-07-28) — novo
`PortfolioValueChip` usa `portfolio.total_cost` real do backend e exibe chip
neutro de variação (sem `current_price`/histórico, a variação não é inventada).

**Encontrado em:** auditoria de paridade visual do redesign ISA-101 (sessão de
2026-07-27, branch `sprint-1-onboarding-usabilidade`).

**Problema:** o header de `pages/investimentos.vue` mostrava "R$ 187.400" (total) e
"+14,2%" (variação) como texto fixo no template — não eram derivados de
`investments`/`portfolio` (dados reais do usuário).

---

### `orcamento.vue` — `spentRatio ?? 0` conflate "sem orçamento" com "0% gasto"

**Encontrado em:** code review do plano do Sprint 2 (sessão de 2026-07-28, branch
`sprint-1-onboarding-usabilidade`), aceito como risco conhecido antes do Green e
ainda não endereçado.

**Problema:** `budgetSpentRatio()` (`composables/useBudgetKpis.ts`) retorna `null`
corretamente quando `allocated <= 0` (sem orçamento definido), mas
`pages/orcamento.vue:118` faz `budgetSpentRatio(...) ?? 0` antes de passar pro
`InstrumentReadout`. Resultado: uma categoria sem limite definido mas com gasto
lançado (`spent > 0`, `allocated = 0`) mostra a mesma barra "0% gasto" de uma
categoria realmente zerada — visualmente indistinguíveis.

**Prioridade:** baixa-média — não é dado incorreto (matemática está certa), mas é
ambiguidade visual num critério que o usuário precisa distinguir rápido no
dia a dia (orçamento zerado vs. orçamento inexistente).

**Critério de aceite:** `InstrumentReadout` (ou `orcamento.vue`) trata o `null` de
`budgetSpentRatio` como estado distinto de "0%" — ex: badge/texto "sem orçamento
definido" em vez de barra vazia — em vez de forçar `?? 0`.

---

## Backlog priorizado de execução (auditorias 2026-07-27 a 2026-07-29)

> Achados confirmados por leitura direta do código, não por suposição.
> Atualizar a coluna Status a cada sessão que tocar um destes itens — este
> backlog é vivo, não um snapshot congelado da auditoria.

**Nota de escopo:** este detalhamento item-a-item cabe aqui enquanto o volume
for pequeno (11 achados). Quando `OBS-1` for ativado e o agente começar a
gerar dezenas/centenas de findings automáticos, o detalhamento migra para
`reports/debt-register.md` (já existe, já é o destino desenhado para isso —
auto-gerado a cada run de `agent-full-report.yml`) ou GitHub Issues/Projects.
Este roadmap volta a conter só iniciativas e objetivos por sprint, não a
lista completa de findings — mantendo seu papel de documento estratégico.

**Prioridade** (P0 bloqueia uso real/dado financeiro hoje · P1 risco/fricção
real, não bloqueia o dia a dia · P2 polimento/dívida técnica de baixo risco)
é independente de **Sprint** (ordem de execução): um P1 pode rodar antes de um
P0 se ele desbloquear ou barateizar os demais (caso de OBS-1 abaixo).

Domínios **Arquitetura** e **Performance**: nenhum achado aberto confirmado
nesta rodada (grep de padrões arriscados + leitura de código não achou nada)
— não incluídos abaixo para não inventar item sem evidência.

### Visão geral

| ID | Domínio | Prioridade | Risco | Valor | Esforço | Owner | Status | Sprint | Source | Validação |
|----|---------|:---:|:---:|:---:|:---:|---|:---:|:---:|---|---|
| OBS-1 | Observabilidade | P1 | Baixo | Alto | M | DevOps | Todo | **0** | User Request | QA (dry-run) + Produção |
| FIN-1 | Financeiro | **P0** | Alto | Muito alto | L | Backend | Todo | 1 | Manual Audit | Automatizado + Fixture |
| FIN-2 | Financeiro | P1 | Médio | Alto | M | Backend | Todo | 1 | Manual Audit | Automatizado + Fixture |
| UX-1 | UX | P1 | Médio | Alto | S | Frontend | Todo | 1 | Manual Audit | Automatizado + Manual |
| SEC-1 | Segurança | P1 | Médio | Alto | L | Backend | Todo | 2 | Manual Audit | Automatizado + Manual |
| UX-2 | UX | P1 | Baixo | Médio | S | Frontend | Todo | 2 | Manual Audit | Manual |
| SEC-2 | Segurança | P2 | Baixo | Médio | M | Backend | Todo | 3A | Manual Audit | Automatizado + Manual |
| FIN-3 | Financeiro | P2 | Baixo | Baixo | S | Frontend | Todo | 3A | Bug Report | Automatizado |
| UX-3 | UX | P2 | Baixo | Baixo | XS | Frontend | Todo | 3B | Manual Audit | Manual |
| UX-4 | UX | P2 | Baixo | Baixo | S | Frontend | Todo | 3B | Manual Audit | Manual |
| UX-5 | UX | P2 | Baixo | Baixo | XS | Frontend | Todo | 3B | Manual Audit | Manual/Decisão |

**Progresso**

```
Total   ░░░░░░░░░░  0%  (0/11 done)
P0      ░░░░░░░░░░  0%  (0/1 done)
P1      ░░░░░░░░░░  0%  (0/5 done)
P2      ░░░░░░░░░░  0%  (0/5 done)
```

### Sprint 0 — Observabilidade primeiro

Ativar o agente de relatório **antes** de começar a mexer em código —
qualquer mudança feita a partir daqui já entra no histórico/tendência do
sistema de auditoria automática, em vez de nascer sem rastro.

**OBS-1 [P1 · Risco Baixo · Valor Alto · Owner DevOps · Source: User Request]** — Agente de relatório
estruturado construído em 2026-07-29, não commitado nem ativado.
- **Onde:** `.github/workflows/{agent-pr-review,agent-full-report}.yml`, `.github/claude-prompts/`, `.github/scripts/`, `reports/`, `docs/adrs/` — todos untracked.
- **Dependências:** nenhuma técnica; requer decisão do usuário sobre commitar.
- **Critério de aceite (execução, não desenho):**
  1. Commit dos arquivos já criados.
  2. Secret `CLAUDE_CODE_OAUTH_TOKEN`/`anthropic_api_key` configurado no repo.
  3. GitHub → Settings → Actions: "Allow GitHub Actions to create and approve pull requests" + "Read and write permissions" habilitados.
  4. Confirmar `environment: production` nos Deployments do Vercel↔GitHub.
- **Validação:** `workflow_dispatch` de `agent-full-report.yml` em modo `fast` (QA/dry-run) → confirmar PR automático com `reports/` preenchido (produção).

### Sprint 1 — Desbloqueio de uso real (Financeiro + Onboarding)

**FIN-1 [P0 · Risco Alto · Valor Muito alto · Owner Backend · Source: Manual Audit]** — Import de PDF só cobre Itaú — Nubank/BTG sem adapter.
- **Onde:** `app/services/pdf_adapters/registry.rb` (`ADAPTERS = [ItauExtratoAdapter, ItauFaturaAdapter]`).
- **Impacto:** contas Nubank/BTG já cadastradas na família não importam PDF — uso real bloqueado.
- **Dependências:** nenhuma. Bloqueia UX-1.
- **Critério de aceite:** `NubankFaturaAdapter` e `BtgExtratoAdapter` registrados, com teste de parsing, PDFs de exemplo importam sem erro.
- **Validação:** RSpec com fixture de PDF real/sintética por banco.

**FIN-2 [P1 · Risco Médio · Valor Alto · Owner Backend · Source: Manual Audit]** — Import CSV exige colunas/formato fixo em português.
- **Onde:** `app/services/csv_import_service.rb` (linhas 37-44: `row["Data"]`/`row["Descrição"]`/`row["Valor"]`, `Date.strptime(..., "%d/%m/%Y")` hardcoded).
- **Impacto:** CSV de banco com nomes de coluna/formato de data diferente falha ou quebra.
- **Dependências:** nenhuma; roda em paralelo com FIN-1.
- **Critério de aceite:** CSV de pelo menos 2 formatos de exportação diferentes importa sem reformatação manual.
- **Validação:** RSpec com fixture por formato de CSV.

**UX-1 [P1 · Risco Médio · Valor Alto · Owner Frontend · Source: Manual Audit]** — Onboarding oferece 6 bancos como "conectáveis", só Itaú funciona; badges com letra hardcoded.
- **Onde:** `pages/onboarding.vue` (array `banks`, badges `label:'N'/'BTG'/...` em vez de `UiBankIcon`, já usado em `contas.vue`).
- **Dependências:** depende de FIN-1 estar concluído (lista de bancos ofertados deve refletir adapters reais).
- **Critério de aceite:** onboarding só lista como "conectável" banco com adapter implementado; badges usam `UiBankIcon`.
- **Validação:** teste de componente (Vitest) + conferência visual manual.

### Sprint 2 — Segurança de conta + comunicação de sessão

**SEC-1 [P1 · Risco Médio · Valor Alto · Owner Backend · Source: Manual Audit]** — Não existe fluxo de recuperação de senha ("esqueci minha senha").
- **Onde:** `config/routes.rb`/`users_controller.rb` só tem troca de senha autenticada (exige `current_password`); sem mailer, sem token de reset, sem rota pública.
- **Impacto:** usuário que esquece a senha fica sem saída própria.
- **Dependências:** confirmar que há mecanismo de envio de e-mail configurado no Rails (ActionMailer/SMTP) antes de estimar — não verificado nesta rodada.
- **Critério de aceite:** usuário solicita reset por e-mail, recebe link com token de expiração curta, define nova senha sem precisar da antiga.
- **Validação:** RSpec (geração/expiração de token) + teste manual do fluxo de e-mail ponta a ponta.

**UX-2 [P1 · Risco Baixo · Valor Médio · Owner Frontend · Source: Manual Audit]** — Sessão expirada redireciona ao login silenciosamente, sem aviso.
- **Onde:** `composables/useApi.ts` (`onResponseError` no 401: zera token + `navigateTo('/login')`, sem toast).
- **Dependências:** nenhuma.
- **Critério de aceite:** usuário vê mensagem "sua sessão expirou" antes/ao ser redirecionado ao login.
- **Validação:** teste manual (forçar 401).

### Sprint 3A — Estabilidade e Segurança

**SEC-2 [P2 · Risco Baixo · Valor Médio · Owner Backend · Source: Manual Audit]** — JWT sem refresh, só expiração fixa de 30 dias (`app/services/jwt_service.rb`, `EXPIRY = 30.days`; `token_version` invalida no logout, mas não é refresh token). Aceitável para uso solo hoje; endereçar antes de multiusuário futuro. **Critério de aceite:** decisão registrada (aceitar o risco documentadamente, ou implementar refresh token). **Validação:** RSpec + teste manual.

**FIN-3 [P2 · Risco Baixo · Valor Baixo · Owner Frontend · Source: Bug Report]** — `orcamento.vue` — `budgetSpentRatio ?? 0` conflate "sem orçamento" com "0% gasto". Ver detalhe completo na seção do bug acima (critério de aceite já escrito lá). **Validação:** Vitest.

### Sprint 3B — UX e Dívida Técnica

**UX-3 [P2 · Risco Baixo · Valor Baixo · Owner Frontend · Source: Manual Audit]** — 3 tokens de `tokens.css` ainda provisórios (`--ly2`, `--t4`, `--blt`, comentário "extrapolado"). **Critério de aceite:** valores conferidos contra o draft aprovado e fixados. **Validação:** comparação visual manual.

**UX-4 [P2 · Risco Baixo · Valor Baixo · Owner Frontend · Source: Manual Audit]** — `KpiCard.vue`/`DebtAlarmBanner.vue` sem media query própria, dependem só do grid do pai colapsar. **Critério de aceite:** os dois componentes não quebram em viewport estreito (~360px). **Validação:** teste manual de resize.

**UX-5 [P2 · Risco Baixo · Valor Baixo · Owner Frontend · Source: Manual Audit]** — `components/charts/PatrimonioTimeline.vue` órfão, com `MOCK_DATA`, não importado em nenhuma página. **Dependências:** decisão do usuário — remover (recomendado, YAGNI) ou implementar de verdade. **Validação:** decisão manual + confirmação de bundle.

---

## Fora de escopo deste roadmap (não confundir)

- Tema claro (dark-only hoje) — é backlog de design, não impacta a lógica financeira
- `/configuracoes` sem link de navegação — é ajuste de UI, resolver quando conveniente
- Autocomplete de bancos brasileiros (`@edusites/bancos-brasil` já instalado, não usado) — nice-to-have, não bloqueia nenhuma lacuna acima
- Remoção do stack legado (Streamlit/Next.js) — fazer em paralelo, não é pré-requisito de nenhum item

---

*Documento de referência para handoff com Claude Code. Gerado em 2026-07-06 a partir da
análise manual de fluxo de caixa, fixos x cartões, rotina x pontual, e prioridade de
quitação conduzida em julho/2026. Auditado em 2026-07-27 (leitura direta de código em
`apps/klipper-api` e `apps/klipper-web`, via agentes Explore em worktrees isoladas):
todas as 6 lacunas confirmadas como implementadas.*
