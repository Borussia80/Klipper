# Roadmap — Klipper Wealth OS

**Gerado em:** 2026-07-06
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

**Estado atual:** `/importar` (beta) só aceita CSV com auto-categorização por regras.

**Necessidade real:** ler PDF de extrato de conta-corrente (Itaú) e fatura de cartão (Itaú Personnalité, Santander, Nubank), cada um com layout diferente.

**Critério de aceite:**
- Upload de PDF → extração de linhas (data, descrição, valor, saldo quando houver) → tela de preview antes de confirmar import (igual ao fluxo de CSV já existente)
- Suporta pelo menos 2 layouts de origem distintos (extrato de conta Itaú + fatura de cartão Itaú) via um padrão de "adapter por instituição" — não um parser único genérico, porque cada banco formata diferente
- Falha de parsing mostra erro claro (linha/página) em vez de importar dado incorreto silenciosamente

**Nota técnica:** cada instituição financeira precisa de um adapter próprio (`ItauExtratoAdapter`, `ItauFaturaAdapter`, `SantanderFaturaAdapter`, `NubankFaturaAdapter`). Resista à tentação de um parser universal — a experiência de campo (esta análise manual) mostrou que os leiautes variam bastante mesmo dentro do mesmo banco (extrato de conta ≠ fatura de cartão).

---

## Lacuna 1.5 — Deduplicação de importação

**Prioridade:** Alta — bloqueia confiar o uso real no Klipper assim que a Lacuna 1 estiver no ar.

**Estado atual:** Nenhum mecanismo de deduplicação ou rastreio de qual arquivo/período já foi
importado. Isso apareceu na prática durante a análise manual desta sessão: um extrato de junho
reimportado junto com um extrato que ia de junho a julho geraria linhas duplicadas se importado
sem cuidado manual.

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

**Estado atual:** `/contas` trata conta/cartão sem vincular a uma pessoa física. Não há como saber, num cartão família, se o gasto foi do Roberto, da Clareana ou da Lara.

**Necessidade real:** cada lançamento (principalmente os de cartão) precisa carregar um portador.

**Critério de aceite:**
- Nova entidade `portador` (ou `membro_familia`): nome, relação (titular/dependente)
- Cada `transacao` ganha uma FK opcional para `portador` (opcional porque nem toda transação tem portador definido, ex: PIX de conta corrente)
- Import de fatura de cartão (Lacuna 1) já popula o portador automaticamente quando o PDF identifica o nome do titular do cartão (a maioria das faturas já traz isso por seção)
- Relatórios e dashboard podem filtrar por portador

---

## Lacuna 3 — Classificação Fixo × Cartão/Parcelamento × Variável, e Rotineiro × Pontual

**Prioridade:** Média-alta.

**Estado atual:** `/orcamento` já é estilo envelope por categoria, mas não tem essa camada de classificação por natureza e por regularidade.

**Necessidade real:** replicar a lógica validada manualmente nesta análise — separar o que é compromisso fixo (pensão, aluguel, terapia, contas) do que é cartão/parcelamento (alavanca real de ajuste) e do que é variável; e separar o que é rotineiro (aparece na maioria dos meses) do que é pontual (evento isolado, tipo viagem ou quitação de financiamento).

**Critério de aceite:**
- Campo `natureza` na categoria: `fixo` / `cartao_parcelamento` / `variavel`
- Campo calculado `recorrencia` por categoria/lançamento recorrente: `rotineiro` (presente em ≥60% dos últimos N meses) / `ocasional` (30-60%) / `pontual` (<30%) — mesmo critério usado manualmente nesta análise
- Dashboard mostra o split fixo × cartão × variável (equivalente ao gráfico de pizza que já fizemos na planilha)
- Tela de categoria mostra "presente em X dos últimos Y meses" para o usuário decidir se algo é rotina ou não

---

## Lacuna 4 — Reembolso de convênio vinculado ao gasto de terapia

**Prioridade:** Média.

**Necessidade real:** vincular lançamentos de despesa (ex: pagamento a terapeuta) a lançamentos de receita (reembolso do convênio), calculando % de cobertura ao longo do tempo — hoje isso só existe porque foi calculado manualmente na planilha.

**Critério de aceite:**
- Tag/vínculo entre uma categoria de despesa (ex: "Terapia Pedro") e uma categoria de receita (ex: "Reembolso Bradesco")
- Card ou tela mostrando: gasto no período, reembolsado no período, % de cobertura, e alerta visual se a cobertura cair muito abaixo da média histórica

---

## Lacuna 5 — Comparador de custo de dívida entre cartões (priorização de quitação)

**Prioridade:** Baixa-média (evento infrequente, mas de alto impacto quando ocorre — como visto nesta análise com a fatura Itaú Personnalité).

**Necessidade real:** dado o saldo em aberto e a taxa de juros do rotativo/parcelamento de cada cartão, ranquear qual quitar primeiro.

**Critério de aceite:**
- Campos por cartão: `saldo_fatura_atual`, `juros_rotativo_am`, `juros_rotativo_aa` (dado que já vem estampado na própria fatura, útil capturar no import da Lacuna 1)
- Tela (ou seção em `/contas`) que ranqueia os cartões por custo do rotativo, do mais caro para o mais barato
- Simulação simples: "se pagar só o mínimo por 1 mês, o saldo sobe para X" — replicando o cálculo que fizemos manualmente para a fatura Itaú

---

## Fora de escopo deste roadmap (não confundir)

- Tema claro (dark-only hoje) — é backlog de design, não impacta a lógica financeira
- `/configuracoes` sem link de navegação — é ajuste de UI, resolver quando conveniente
- Autocomplete de bancos brasileiros (`@edusites/bancos-brasil` já instalado, não usado) — nice-to-have, não bloqueia nenhuma lacuna acima
- Remoção do stack legado (Streamlit/Next.js) — fazer em paralelo, não é pré-requisito de nenhum item

---

*Documento de referência para handoff com Claude Code. Baseado na análise manual de fluxo de caixa, fixos x cartões, rotina x pontual, e prioridade de quitação conduzida em julho/2026.*
