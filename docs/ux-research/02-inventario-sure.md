# 02 — Inventário: Sure (fork comunitário do Maybe Finance)

**Licença:** AGPL-3.0 → **sala limpa.** Nada de código, CSS, templates ou estrutura de arquivos.
**Papel no Klipper:** linguagem visual de telas desktop (patrimônio, contas, gráficos de saldo, sobriedade).

## Estado da observação — leia antes

| Fonte | Situação |
|---|---|
| Instância em execução (`[URL_SURE]`) | **Não observada.** A URL ficou como placeholder no pedido, e o README não aponta demo pública utilizável |
| Prints (`prints/sure/`) | **Não existem** — a pasta foi criada vazia |
| Documentação pública | Lida: README do repositório (só o texto) e site oficial `sure.am` citado no README |

Por isso este inventário tem **dois níveis de confiança**:

- **[DOC]** — afirmado pela documentação pública.
- **[A OBSERVAR]** — hipótese de trabalho sobre o que provavelmente existe, escrita para orientar a sessão de
  observação. **Não deve virar decisão de design antes de confirmada na interface ou em print.**

## O que a documentação afirma

- **[DOC]** App de finanças pessoais completo, auto-hospedável em Docker; acessível por navegador, app desktop
  macOS, app mobile, API e agentes LLM.
- **[DOC]** O print do README mostra um painel com **fluxo de caixa, patrimônio líquido, gastos e saídas**, ao lado
  de um assistente de IA.
- **[DOC]** Inclui assistente de IA opcional.
- **[DOC]** "Maybe" é marca registrada da Maybe Finance, Inc.; nome e logo não podem ser usados por forks.
- **[DOC]** O README não cita bibliotecas de ícones nem fontes.

## Telas a observar (escopo de finanças pessoais)

Para cada tela, o que registrar na sessão de observação: propósito, hierarquia (o que o olho encontra primeiro),
componentes, interações, os quatro estados (carregando, vazio, erro, sucesso) e como reflui em 390 px.

| # | Tela | Por que interessa ao Klipper | Perguntas para a observação |
|---|---|---|---|
| S1 | **Painel / patrimônio** [DOC: existe] | Referência principal para o novo painel desktop | Qual é o número-herói? Há seletor de período no gráfico? Como ativos e passivos aparecem separados? Onde fica o fluxo de caixa? Quanto espaço em branco por bloco? |
| S2 | **Lista de contas agrupada por tipo** [A OBSERVAR] | O `/contas` do Klipper é lista plana | As contas são agrupadas (corrente, cartão, investimento, dívida)? Subtotal por grupo? Como mostra conta desatualizada? |
| S3 | **Detalhe de conta com gráfico de saldo** [A OBSERVAR] | Klipper não tem saldo histórico por conta | Gráfico de linha ou área? Linha de base em zero? Como trata período sem dado? Tabela de transações embaixo? |
| S4 | **Transações** [DOC: categorização citada por terceiros] | Comparar densidade com o `/transacoes` | Agrupamento por dia? Colunas no desktop? Edição inline ou painel lateral? Seleção em massa? |
| S5 | **Orçamento** [A OBSERVAR] | Comparar com envelopes do Klipper | Visual de progresso por categoria? Como sinaliza excesso? |
| S6 | **Importação CSV** [A OBSERVAR] | Klipper já tem; interessa o mapeamento de colunas | Passo a passo ou tela única? Prévia antes de gravar? |
| S7 | **Configurações** [A OBSERVAR] | Organização em seções | Navegação lateral própria? |

## Elementos de linguagem visual a medir (não copiar)

Na sessão de observação, **medir e anotar com palavras próprias**, para alimentar `04-design-tokens.md`:

> A paleta do Klipper não muda (decisão de 2026-10-17). Medir serve só para entender densidade e hierarquia.

- Tom das superfícies (neutro puro, quente ou frio) e quantos níveis de elevação existem.
- Densidade: altura de linha de tabela, espaço entre blocos do painel.
- Tipografia: número de tamanhos em uso, se números usam algarismos tabulares, peso do número-herói.
- Uso de cor: quantas cores aparecem numa tela "normal" (sem alarme). Hipótese a confirmar: sobriedade alta, cor
  concentrada em gráficos e em variação positiva/negativa — o que **conflita** com a regra de cor do Klipper
  (variação verde/vermelha em tudo é ruído; ver `03-matriz-referencias.md`).
- Raios e sombras: cantos arredondados grandes ou pequenos? Sombra ou borda?
- Família tipográfica e biblioteca de ícones: identificar **pela interface** (inspeção visual) e, se forem abertas,
  usar a partir da fonte original — ver `07-registro-pi.md`.

## O que já se pode afirmar como intenção (independente da observação)

O Klipper quer do Sure **a postura**, não os valores: painel desktop com um número dominante (patrimônio), gráfico
de evolução logo abaixo, contas agrupadas com subtotal, muito ar entre blocos e pouca decoração. É o que as
specs de `05-specs/` assumem; a pele é a náutica do Klipper.
