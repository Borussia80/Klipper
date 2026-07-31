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

## Backlog priorizado de execução (produto + segurança, auditorias 2026-07-27 a 2026-07-29)

> Roadmap único — não existe roadmap de produto e roadmap de segurança em
> paralelo. Cada item carrega duas etiquetas independentes: **Categoria**
> (Segurança/Financeiro/UX/Observabilidade/Arquitetura) e **Prioridade**
> (P0/P1/P2). **Sprint** é a ordem de execução real e é campo separado da
> Prioridade — um P1 pode rodar antes de um P0 se desbloquear os demais
> (caso de OBS-1). Atualizar a coluna Status a cada sessão que tocar um
> destes itens — este backlog é vivo.

**IDs de segurança:** os achados da auditoria de segurança de 2026-07-29 têm
ID técnico próprio (`H1`, `M3`, `L7`...) documentado em
[`docs/security/audit-2026-07-29.md`](docs/security/audit-2026-07-29.md) —
esse arquivo é um **snapshot imutável**, não editar para refletir progresso.
No roadmap, cada achado ganha um ID próprio de backlog (`SEC-01`...`SEC-16`,
namespace único, sem colidir com IDs de auditorias futuras) e a coluna
**Origem** aponta de volta para o ID técnico — é o de-para entre os dois
documentos. Os 10 achados de severidade Low (`L1`-`L10`, robustez de baixo
risco) são agrupados por tema em 3 itens (`SEC-14`/`SEC-15`/`SEC-16`) para não
inflar a tabela — os IDs individuais continuam existindo, só que no arquivo
de auditoria, não aqui.

Domínios **Arquitetura** e **Performance**: nenhum achado aberto confirmado
nesta rodada — não incluídos abaixo para não inventar item sem evidência.

### Visão geral

| ID | Categoria | Origem | Prioridade | Risco | Valor | Esforço | Owner | Status | Sprint | Source | Validação |
|----|---|---|:---:|:---:|:---:|:---:|---|:---:|:---:|---|---|
| OBS-1 | Observabilidade | Manual Audit (roadmap original) | P1 | Baixo | Alto | M | DevOps | Todo | **0** | User Request | QA (dry-run) + Produção |
| FIN-1 | Financeiro | Manual Audit (roadmap original) | **P0** | Alto | Muito alto | L | Backend | **Done** | 1 | Manual Audit | Automatizado + Fixture |
| SEC-03 | Segurança | H1 | **P0** | Alto | Alto | M | Backend | **Done** | 1 | Security Audit | **PoC (request spec)** + Automatizado |
| SEC-04 | Segurança | H2 | **P0** | Alto | Alto | M | Backend | **Done** | 1 | Security Audit | **PoC (request spec)** + Automatizado |
| SEC-05 | Segurança | H3 | **P0** | Alto | Alto | M | Backend | **Done** | 1 | Security Audit | **PoC (request spec)** + Automatizado |
| FIN-2 | Financeiro | Manual Audit (roadmap original) | P1 | Médio | Alto | M | Backend | **Done** | 2 | Manual Audit | Automatizado + Fixture |
| UX-1 | UX | Manual Audit (roadmap original) | P1 | Médio | Alto | S | Frontend | **Done** | 2 | Manual Audit | Automatizado + Manual |
| SEC-06 | Segurança | H4 | P2 | Baixo | Baixo | S | Backend | **Done** | 2 | Security Audit | Decisão + bump de gem |
| SEC-14 | Segurança | L1+L2+L4+L5 | P2 | Baixo | Baixo | M | Backend | **Done** | 2 | Security Audit | RSpec (erro por linha) + teste manual |
| SEC-01 | Segurança | Manual Audit (roadmap original) | P1 | Médio | Alto | L | Backend | **Done** | 3 | Manual Audit | Automatizado + Manual |
| UX-2 | UX | Manual Audit (roadmap original) | P1 | Baixo | Médio | S | Frontend | **Done** | 3 | Manual Audit | Manual |
| SEC-07 | Segurança | M1 | P1 | Médio | Médio | S | Backend | **Done** | 3 | Security Audit | RSpec (token_version pós-troca) |
| SEC-08 | Segurança | M2 | P1 | Médio | Médio | M | Backend | **Done** | 3 | Security Audit | Teste manual (throttle) + RSpec |
| SEC-09 | Segurança | M3 | P1 | Baixo | Médio | XS | Backend | **Done** | 3 | Security Audit | Teste manual (redirect HTTPS) |
| SEC-02 | Segurança | Manual Audit (roadmap original) | P2 | Baixo | Médio | M | Backend | **Done** | 4 | Manual Audit | Decisão registrada |
| SEC-10 | Segurança | M4 | P2 | Baixo | Baixo | XS | Backend | **Done** | 4 | Security Audit | `bundler-audit` limpo |
| SEC-11 | Segurança | M5 | P2 | Baixo | Baixo | S | Frontend | **Done** | 4 | Security Audit | `npm audit` limpo |
| SEC-12 | Segurança | M6 | P2 | Baixo | Médio | S | Frontend | **Done** | 4 | Security Audit | Decisão registrada |
| SEC-13 | Segurança | M7 | P2 | Baixo | Médio | S | DevOps | **Done** | 4 | Security Audit | Revisão de permissões do workflow |
| SEC-15 | Segurança | L7+L8+L9 | P2 | Baixo | Baixo | S | DevOps | **Parcial** | 4 | Security Audit | Revisão manual + Dependabot ativo |
| SEC-16 | Segurança | L3+L6+L10 | P2 | Baixo | Baixo | S | Backend | **Done** | 4 | Security Audit | RSpec (timing) + teste manual |
| FIN-3 | Financeiro | Bug Report | P2 | Baixo | Baixo | S | Frontend | **Done** | 5 | Bug Report | Automatizado |
| UX-3 | UX | Manual Audit (roadmap original) | P2 | Baixo | Baixo | XS | Frontend | **Done** | 5 | Manual Audit | Manual |
| UX-4 | UX | Manual Audit (roadmap original) | P2 | Baixo | Baixo | S | Frontend | **Done** | 5 | Manual Audit | Manual |
| UX-5 | UX | Manual Audit (roadmap original) | P2 | Baixo | Baixo | XS | Frontend | **Done** | 5 | Manual Audit | Manual/Decisão |

**Progresso**

```
Total   █████████░  92%  (23/25 done)
P0      ██████████  100%  (4/4 done)
P1      █████████░  88%  (7/8 done)
P2      █████████░  92%  (12/13 done)
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

### Sprint 1 — Segurança crítica + uso real

Os três achados de BOLA/IDOR abaixo (SEC-03/04/05) entram antes de qualquer
outra coisa: são P0, permitem que um usuário leia ou altere dado de outro
usuário, e três subsistemas independentes (orçamento, transações/
investimentos, importação) foram encontrados com o mesmo padrão de falha —
alta confiança de que é um problema sistêmico, não um caso isolado.

**SEC-03 [P0 · Risco Alto · Valor Alto · Owner Backend · Origem: H1 · Source: Security Audit · Status: Done]** — BOLA: `Budget` aceita `category_id` de outro usuário, exposto via `BudgetEngine#summary`.
- **Onde:** `app/controllers/api/v1/budgets_controller.rb` (`budget_params` sem revalidação) + `app/services/budget_engine.rb#summary` (linhas 25-27, expõe `category.name`/`icon`/`natureza` do FK não validado). Detalhe completo em [`docs/security/audit-2026-07-29.md#h1`](docs/security/audit-2026-07-29.md).
- **Critério de aceite (nesta ordem):**
  1. **PoC de reprodução cross-user** — request spec com 2 usuários: usuário A cria budget com `category_id` de uma categoria do usuário B; confirmar que `GET /budgets/summary` de A retorna `category_name`/`category_icon`/`natureza` de B. Isso confirma o problema é reproduzível e que nenhuma outra camada de proteção (ex: validação de model) já bloqueia o caso.
  2. Só então: revalidar `category_id` contra `current_user.categories` em `create`/`update` de `budgets_controller.rb`.
- **Validação:** RSpec (request spec do PoC vira o teste de regressão do fix).

**SEC-04 [P0 · Risco Alto · Valor Alto · Owner Backend · Origem: H2 · Source: Security Audit · Status: Done]** — BOLA: `Transaction`/`Investment` aceitam `account_id`/`category_id`/`member_id` de outro usuário.
- **Onde:** `app/controllers/api/v1/transactions_controller.rb#update` + `app/controllers/api/v1/investments_controller.rb#create`/`#update` (FKs de `transaction_params`/`investment_params` sem revalidação). Detalhe completo em [`docs/security/audit-2026-07-29.md#h2`](docs/security/audit-2026-07-29.md).
- **Critério de aceite (nesta ordem):**
  1. **PoC de reprodução cross-user** — request spec: usuário A edita uma transação/investimento próprio setando `account_id`/`member_id` de B; confirmar que o registro passa a aparecer nos totais da conta de B.
  2. Só então: revalidar cada FK contra `current_user.<associação>` em ambos os controllers.
- **Validação:** RSpec (request spec do PoC vira o teste de regressão do fix).

**SEC-05 [P0 · Risco Alto · Valor Alto · Owner Backend · Origem: H3 · Source: Security Audit · Status: Done]** — Mesmo padrão de BOLA no fluxo de importação (CSV/PDF).
- **Onde:** `app/controllers/api/v1/imports_controller.rb` → `CsvImportService`/`PdfImportService` → `BankImport::TransactionWriter#write!` (não valida `account_id`/`member_id` contra `@user`). Detalhe completo em [`docs/security/audit-2026-07-29.md#h3`](docs/security/audit-2026-07-29.md).
- **Critério de aceite (nesta ordem):**
  1. **PoC de reprodução cross-user** — request spec: usuário A importa um CSV informando `account_id` de B; confirmar que a transação é gravada contra a conta de B.
  2. Só então: validar `account_id`/`member_id` dentro de `BankImport::TransactionWriter#write!` (ponto único, reusado por CSV e PDF).
- **Validação:** RSpec (request spec do PoC vira o teste de regressão do fix).

**FIN-1 [P0 · Risco Alto · Valor Muito alto · Owner Backend · Source: Manual Audit · Status: Done]** — Import de PDF só cobria Itaú — Nubank/BTG sem adapter.
- **Onde:** `app/services/pdf_adapters/registry.rb` (`ADAPTERS = [ItauExtratoAdapter, ItauFaturaAdapter, NubankFaturaAdapter, BtgExtratoAdapter]`).
- **Impacto:** contas Nubank/BTG já cadastradas na família não importavam PDF — uso real bloqueado.
- **Dependências:** nenhuma. Desbloqueia UX-1.
- **Critério de aceite:** `NubankFaturaAdapter` e `BtgExtratoAdapter` registrados, com teste de parsing, PDFs de exemplo importam sem erro.
- **Validação:** RSpec com fixture de PDF real por banco.
- **Progresso:** `NubankFaturaAdapter` — parser de fatura (coluna única, ano inferido pela data de emissão), testado contra fixture real (`Modelo_Bancos/Nubank_2026-07-10.pdf`) e casos sintéticos (titular, seção "Pagamentos" sem titular, virada de ano). `BtgExtratoAdapter` — parser da seção "Conta corrente - Movimentação" do extrato de conta investimento (única seção do relatório equivalente a um ledger de lançamentos; as demais são posição de carteira), testado contra fixture real (`Modelo_Bancos/report_146828241.pdf`) e casos sintéticos; contorna um bug do PDF gerado pelo BTG (ToUnicode CMap incompleto mapeia a letra "a" minúscula como NUL em títulos/cabeçalhos — não afeta as linhas de dados).

### Sprint 2 — Importação e UX

**FIN-2 [P1 · Risco Médio · Valor Alto · Owner Backend · Source: Manual Audit · Status: Done]** — Import CSV exige colunas/formato fixo em português.
- **Onde:** `app/services/csv_import_service.rb` (`row["Data"]`/`row["Descrição"]`/`row["Valor"]`, `Date.strptime(..., "%d/%m/%Y")` hardcoded).
- **Impacto:** CSV de banco com nomes de coluna/formato de data diferente falha ou quebra.
- **Dependências:** nenhuma; roda em paralelo com FIN-1.
- **Critério de aceite:** CSV de pelo menos 2 formatos de exportação diferentes importa sem reformatação manual.
- **Validação:** RSpec com fixture por formato de CSV.

**UX-1 [P1 · Risco Médio · Valor Alto · Owner Frontend · Source: Manual Audit · Status: Done]** — Onboarding oferece 6 bancos como "conectáveis", só Itaú funciona; badges com letra hardcoded.
- **Onde:** `pages/onboarding.vue` (array `banks`, badges `label:'N'/'BTG'/...` em vez de `UiBankIcon`, já usado em `contas.vue`).
- **Dependências:** depende de FIN-1 estar concluído (lista de bancos ofertados deve refletir adapters reais).
- **Critério de aceite:** onboarding só lista como "conectável" banco com adapter implementado; badges usam `UiBankIcon`.
- **Validação:** teste de componente (Vitest) + conferência visual manual.

**SEC-06 [P2 · Risco Baixo · Valor Baixo · Owner Backend · Origem: H4 · Source: Security Audit · Status: Done]** — CVE `activestorage 8.1.3` (mitigado, não usado ativamente). Detalhe em [`docs/security/audit-2026-07-29.md#h4`](docs/security/audit-2026-07-29.md). **Critério de aceite:** bump para `>= 8.1.3.1` ou aceite de risco documentado. **Validação:** `bundler-audit` limpo para esta gem.

**SEC-14 [P2 · Risco Baixo · Valor Baixo · Owner Backend · Origem: L1+L2+L4+L5 · Source: Security Audit · Status: Done]** — Robustez de importação: exceção não tratada no parser de CSV (`ArgumentError` em `AmountParser`), exceção não tratada no `#preview` de PDF, sem limite de tamanho de arquivo, sem validação de magic bytes. Detalhe de cada achado em [`docs/security/audit-2026-07-29.md`](docs/security/audit-2026-07-29.md). **Critério de aceite:** os 4 achados corrigidos (rescue específico + limite de tamanho + checagem de magic bytes). **Validação:** RSpec com fixture inválida por achado + teste manual.

### Sprint 3 — Autenticação

**SEC-01 [P1 · Risco Médio · Valor Alto · Owner Backend · Source: Manual Audit]** · Status: Done — Não existe fluxo de recuperação de senha ("esqueci minha senha").
- **Onde:** `config/routes.rb`/`users_controller.rb` só tem troca de senha autenticada (exige `current_password`); sem mailer, sem token de reset, sem rota pública.
- **Impacto:** usuário que esquece a senha fica sem saída própria.
- **Dependências:** confirmar que há mecanismo de envio de e-mail configurado no Rails (ActionMailer/SMTP) antes de estimar — não verificado nesta rodada.
- **Critério de aceite:** usuário solicita reset por e-mail, recebe link com token de expiração curta, define nova senha sem precisar da antiga.
- **Validação:** RSpec (geração/expiração de token) + teste manual do fluxo de e-mail ponta a ponta.

**UX-2 [P1 · Risco Baixo · Valor Médio · Owner Frontend · Source: Manual Audit]** · Status: Done — Sessão expirada redireciona ao login silenciosamente, sem aviso.
- **Onde:** `composables/useApi.ts` (`onResponseError` no 401: zera token + `navigateTo('/login')`, sem toast).
- **Dependências:** nenhuma.
- **Critério de aceite:** usuário vê mensagem "sua sessão expirou" antes/ao ser redirecionado ao login.
- **Validação:** teste manual (forçar 401).

**SEC-07 [P1 · Risco Médio · Valor Médio · Owner Backend · Origem: M1 · Source: Security Audit]** · Status: Done — JWT não é revogado na troca de senha (`token_version` só incrementa no logout). Detalhe em [`docs/security/audit-2026-07-29.md#m1`](docs/security/audit-2026-07-29.md). **Critério de aceite:** `users_controller.rb#password` incrementa `token_version` também. **Validação:** RSpec (token emitido antes da troca deixa de ser aceito depois).

**SEC-08 [P1 · Risco Médio · Valor Médio · Owner Backend · Origem: M2 · Source: Security Audit]** · Status: Done — Ausência de rate limiting (`rack-attack` não presente) em `sign_in`/`sign_up`. Detalhe em [`docs/security/audit-2026-07-29.md#m2`](docs/security/audit-2026-07-29.md). **Critério de aceite:** `rack-attack` adicionado com throttle por IP e por e-mail nas duas rotas. **Validação:** teste manual (N tentativas bloqueadas) + RSpec.

**SEC-09 [P1 · Risco Baixo · Valor Médio · Owner Backend · Origem: M3 · Source: Security Audit]** · Status: Done — `force_ssl` desabilitado em produção (`config/environments/production.rb:25`). Detalhe em [`docs/security/audit-2026-07-29.md#m3`](docs/security/audit-2026-07-29.md). **Critério de aceite:** `config.force_ssl = true` habilitado (confirmar antes que não quebra o health check do proxy). **Validação:** teste manual (requisição HTTP redireciona para HTTPS).

### Sprint 4 — Hardening

**SEC-02 [P2 · Risco Baixo · Valor Médio · Owner Backend · Source: Manual Audit]** · Status: Done (risco aceito) — JWT sem refresh, só expiração fixa de 30 dias (`app/services/jwt_service.rb`, `EXPIRY = 30.days`). **Decisão (2026-07-30):** risco aceito documentadamente — uso solo atual não justifica a complexidade de refresh token/rotação. Revisitar este item antes de abrir a conta para multiusuário. **Validação:** decisão registrada no roadmap.

**SEC-10 [P2 · Risco Baixo · Valor Baixo · Owner Backend · Origem: M4 · Source: Security Audit · Status: Done]** — `loofah`/`rails-html-sanitizer` desatualizados — **hardening contínuo**. Detalhe em [`docs/security/audit-2026-07-29.md#m4`](docs/security/audit-2026-07-29.md). **Critério de aceite:** bump inicial (`loofah >= 2.25.2`, `rails-html-sanitizer >= 1.7.1`); depois disso, manutenção passa a ser automática via Dependabot — depende de SEC-15 corrigir a lacuna de ecossistema npm/bundler no `dependabot.yml` para não precisar reaparecer como item de roadmap a cada bump de rotina. **Validação:** `bundler-audit` limpo.

**SEC-11 [P2 · Risco Baixo · Valor Baixo · Owner Frontend · Origem: M5 · Source: Security Audit · Status: Done]** — Dependências npm vulneráveis em `klipper-web`/`quebec-web` (`tar` crítico, `shell-quote`/`svgo` altos) — **hardening contínuo**. Detalhe em [`docs/security/audit-2026-07-29.md#m5`](docs/security/audit-2026-07-29.md). **Critério de aceite:** `npm audit fix` (não-breaking) aplicado nos dois apps; bump breaking de `@nuxt/image` avaliado à parte; manutenção seguinte automática via Dependabot (mesma dependência de SEC-15 que SEC-10). **Validação:** `npm audit --production` limpo (ou só achados aceitos documentadamente).

**SEC-12 [P2 · Risco Baixo · Valor Médio · Owner Frontend · Origem: M6 · Source: Security Audit]** · Status: Done (risco aceito) — JWT em cookie não-`httpOnly` (`useApi.ts`, `useCookie`). Detalhe em [`docs/security/audit-2026-07-29.md#m6`](docs/security/audit-2026-07-29.md). **Decisão (2026-07-30):** risco aceito documentadamente — migrar para `httpOnly` tocaria login/logout/useApi/interceptors inteiro, esforço não justificado pelo perfil de uso solo atual. Revisitar antes de multiusuário. **Validação:** decisão registrada no roadmap.

**SEC-13 [P2 · Risco Baixo · Valor Médio · Owner DevOps · Origem: M7 · Source: Security Audit · Status: Done]** — Risco de prompt injection indireta (LLM01) em `agent-pr-review.yml` (repo público, PRs de fork processados por agente com Bash + `GH_TOKEN`). Detalhe em [`docs/security/audit-2026-07-29.md#m7`](docs/security/audit-2026-07-29.md). **Critério de aceite:** revisar escopo de permissões do `GH_TOKEN` para PRs de fork, ou restringir a `workflow_dispatch` manual para PRs externos. **Validação:** revisão manual da política de permissões do workflow.

**SEC-15 [P2 · Risco Baixo · Valor Baixo · Owner DevOps · Origem: L7+L8+L9 · Source: Security Audit · Status: Parcial (2/3)]** — Robustez de infraestrutura: `config.hosts` irrestrito, GitHub Actions pinadas por tag mutável, Dependabot sem ecossistema `npm`. Detalhe de cada achado em [`docs/security/audit-2026-07-29.md`](docs/security/audit-2026-07-29.md). **Critério de aceite:** os 3 achados corrigidos (`config.hosts` restrito ao domínio de produção; actions pinadas por SHA; `dependabot.yml` com entrada `npm` para `apps/klipper-web` e `apps/quebec-web`). **Feito (2026-07-30):** actions de `ci.yml`, `agent-pr-review.yml` e `agent-full-report.yml` pinadas por SHA de commit; `dependabot.yml` com entradas `npm` para `apps/klipper-web` e `apps/quebec-web`. **Pendente:** `config.hosts` em `config/environments/production.rb` segue irrestrito — bloqueado por não sabermos ainda o hostname de produção do `klipper-api` (checar no dashboard do Render → klipper-api → Settings → Custom Domains). **Validação:** revisão manual + primeiro PR automático do Dependabot no ecossistema npm.

**SEC-16 [P2 · Risco Baixo · Valor Baixo · Owner Backend · Origem: L3+L6+L10 · Source: Security Audit · Status: Done]** — Robustez de aplicação: timing attack em `sign_in`, troca de e-mail sem reautenticação, Service Worker cacheando resposta financeira em disco. Detalhe de cada achado em [`docs/security/audit-2026-07-29.md`](docs/security/audit-2026-07-29.md). **Critério de aceite:** os 3 achados corrigidos (tempo constante em `sign_in`; `current_password` exigido para trocar e-mail; cache do Service Worker excluído das rotas `/api/v1/*` ou revisado). **Validação:** RSpec (timing + reauth) + teste manual (Service Worker).

### Sprint 5 — Polimento

**FIN-3 [P2 · Risco Baixo · Valor Baixo · Owner Frontend · Source: Bug Report · Status: Done]** — `orcamento.vue` — `budgetSpentRatio ?? 0` conflate "sem orçamento" com "0% gasto". Ver detalhe completo na seção do bug acima (critério de aceite já escrito lá). **Validação:** Vitest.

**UX-3 [P2 · Risco Baixo · Valor Baixo · Owner Frontend · Source: Manual Audit · Status: Done]** — 3 tokens de `tokens.css` ainda provisórios (`--ly2`, `--t4`, `--blt`, comentário "extrapolado"). **Decisão:** sem draft aprovado no repo para conferir os valores contra, optou-se por manter os valores como estão (já em uso em produção sem relato de problema) e apenas remover os comentários "extrapolado" que sinalizavam uma pendência inexistente. **Validação:** revisão manual do arquivo (`3b56b5f`).

**UX-4 [P2 · Risco Baixo · Valor Baixo · Owner Frontend · Source: Manual Audit · Status: Done]** — `KpiCard.vue`/`DebtAlarmBanner.vue` sem media query própria, dependem só do grid do pai colapsar. **Feito (1ª passada):** media query própria adicionada aos dois componentes. **Verificação visual (2ª passada, Chrome disponível):** o fix isolado era necessário mas insuficiente — achados adicionais, todos corrigidos:
- `AppSidebar.vue` tinha `display:flex` inline no `<nav>`, que por especificidade sempre vencia a regra `@media(max-width:768px){.shell-nav{display:none}}` em `main.css` — o sidebar nunca colapsava de fato no mobile (bug pré-existente, não introduzido por esta sessão). Regra movida para a classe `.shell-nav`.
- `.shell` (CSS Grid) e `.alarm-txt` (flexbox) sofriam "blowout": sem `min-width:0` explícito, itens de grid/flex não encolhem abaixo do conteúdo intrínseco mesmo em tracks `1fr`, estourando a viewport silenciosamente (`.shell` tem `overflow:hidden`, então nunca aparecia como scroll de página). Corrigido com `min-width:0` em `.shell-header`, `.shell-main` e `.alarm-txt`.
- `AppTopbar.vue` também estourava, independente do grid: bloco da marca reservava `var(--nav)` mesmo com sidebar oculto, e busca/botão "Lançamento" não encolhiam nem quebravam linha. Rótulos de texto (marca, busca, `⌘K`, "Lançamento") agora somem em mobile, mantendo só ícones.
- Corrigir o colapso do sidebar sem repor navegação teria deixado o mobile sem nenhuma forma de trocar de página — regressão funcional, não só visual. Achado o componente `MobileNav.vue` (barra inferior), já existente no repo mas nunca importado em nenhum layout e com tokens de cor legados (`--border`/`--ink-3`/`--accent`/`--space-2`, removidos de `tokens.css`). Decisão levada ao usuário via pergunta direta; escolhida a opção de terminar a integração: tokens remapeados para os atuais (`--bd`/`--t3`/`--t1`+`--brass`), rótulos alinhados aos do sidebar, componente conectado em `app.vue`.

Verificado visualmente em Chrome (~500px, abaixo do breakpoint de 768px): sidebar oculto, barra inferior fixa funcional (navegação entre as 5 rotas, indicador de item ativo, `padding-bottom` do conteúdo não sobrepõe a barra), topbar sem corte, `DebtAlarmBanner` sem clipping. Desktop (1400px) re-verificado sem regressão. 273/273 Vitest, `vue-tsc` sem novos erros vs. baseline. **Validação:** verificação visual manual (Chrome) + testes automatizados.

**UX-5 [P2 · Risco Baixo · Valor Baixo · Owner Frontend · Source: Manual Audit · Status: Done]** — `components/charts/PatrimonioTimeline.vue` órfão, com `MOCK_DATA`, não importado em nenhuma página. **Decisão do usuário:** implementar de verdade, com snapshot mensal daqui pra frente (sem fabricar histórico). **Feito:** não existia histórico real de patrimônio no schema — criada tabela `net_worth_snapshots` (migration + model + validações), `GET /api/v1/reports/net_worth` agora grava/atualiza (upsert) o snapshot do mês corrente a cada chamada, nova rota `GET /api/v1/reports/net_worth_history` (com filtro de período 3m/6m/1a/max) expõe a série para o frontend. `PatrimonioTimeline.vue` reescrito para consumir dados reais via `useReports`, com estado vazio explícito para quem ainda não acumulou ≥2 meses de snapshots (`v-show` em vez de `v-if` para não destruir o nó DOM do React island). Cobertura: 405/405 RSpec, 273/273 Vitest, `vue-tsc` sem novos erros vs. baseline, `npm run build` ok. **Validação:** testes automatizados (backend + frontend); sem histórico fabricado — o gráfico só populará com o uso real ao longo dos meses.

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
