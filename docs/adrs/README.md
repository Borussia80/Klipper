# ADRs (Architecture Decision Records)

`proposed/` contém ADRs gerados automaticamente por
`.github/scripts/draft-adrs.mjs` quando um finding do relatório de auditoria
(`agent-full-report.yml`) é marcado com `adr_candidate: true` — geralmente
recomendações estruturais como remover um módulo, criar um índice ou separar
um serviço.

Um ADR em `proposed/` é **só uma proposta**: `status: proposed` no
front-matter, nunca `accepted`. A decisão de aceitar, rejeitar ou adaptar é
sempre humana. Ao aceitar uma proposta, mova o arquivo para fora de
`proposed/` (ex: `docs/adrs/ADR-<data>-<seq>.md`) e atualize o `status`.

Cada ADR referencia o Finding ID que o originou (ex: `finding: ARCH-018`),
ligando a cadeia achado → proposta → decisão → implementação → próxima
auditoria.
