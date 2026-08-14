# ADR Draft (a partir de um Finding)

Este prompt roda **só quando `draft-adrs.mjs` identifica um finding com
`adr_candidate: true`** ainda sem ADR vinculado, após `merge-findings.mjs` já
ter atribuído o ID permanente. Uma execução por finding elegível.

## Regra inegociável

Mesma regra de `_shared-contract.md`: nunca inferir fatos, nunca inventar
consequência ou alternativa que não seja razoável de derivar do próprio
finding e do código observável no checkout. Sem base suficiente para uma
seção, escreva `Evidence unavailable.` em vez de preencher com genérico.

## Entrada

Você recebe (via variável de ambiente ou arquivo indicado por
`INPUT_FINDING_PATH`) o finding completo já com ID permanente, no formato
definido em `_shared-contract.md`: `id`, `category`, `natural_key`,
`severity`, `evidence`, `description`, `recommendation`, etc.

## O que você NÃO faz

Você não decide o número sequencial do ADR nem o path do arquivo — isso é
`draft-adrs.mjs` (determinístico). Você não marca `status: accepted` — todo
ADR gerado por este prompt nasce `status: proposed`; aceitar é decisão
humana, fora do agente. Você só escreve o **corpo em prosa** do ADR.

## Estrutura de saída

Markdown puro, sem front-matter (o front-matter — `status: proposed`,
`finding: <ID>`, `date` — é escrito por `draft-adrs.mjs`, não por você):

```markdown
# <Título curto e concreto da decisão proposta>

## Contexto

<Por que essa decisão está sendo proposta. Cite o Finding ID e a evidência
observada (arquivo/linha) que motivou a proposta. Sem especulação além do
que o finding e o código sustentam.>

## Decisão proposta

<A mudança estrutural recomendada, de forma concreta e implementável — não
um objetivo vago. Se houver mais de uma alternativa razoável, liste-as
brevemente e indique qual você recomenda e por quê.>

## Consequências

<Trade-offs reais da decisão: o que melhora, o que fica mais caro/arriscado,
o que precisa ser migrado. Se não houver base para avaliar uma consequência
específica (ex: impacto em performance de produção), escreva `Evidence
unavailable.` em vez de assumir.>

## Referência

Finding: `<ID>` (`<natural_key>`)
```

## Saída

Escreva apenas o corpo Markdown acima em `$OUTPUT_PATH` — `draft-adrs.mjs`
monta o arquivo final em `docs/adrs/proposed/ADR-<data>-<seq>.md` combinando
seu corpo com o front-matter determinístico.
