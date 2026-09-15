# Plano de Execução Klipper

**Base:** auditoria de 14 set 2026  
**Escopo:** 17 frentes cobrindo 18 achados, organizadas por urgência de agir.  
**Regra:** todo item segue Red → Green → Refactor; o teste vermelho vem antes do código.

## Faixas

- **Crítica:** irreversível, impede o uso diário ou é portão de segurança/verificação.
- **Alta:** piora com o uso ou deixa parte do produto inacessível.
- **Média:** precisa estar pronta antes do segundo usuário.
- **Baixa:** dívida latente, polimento e documentação.

## Decisões fechadas em 14 set 2026

| ID | Decisão | Consequência |
|---|---|---|
| D1 | Kira sai | Remover `pages/kira.vue` e referências; eventual retorno volta ao roadmap de produto. |
| D2 | SPA | `ssr: false`, mantendo `nuxt build`, Nitro, CSP com nonce e as portas do M2. |
| D3 | Recharts sai | SVG nativo em Vue; remover React, Recharts e dependências da ilha. |

## Crítica

### C1 · Portão frontend (P)

Adicionar ao job web do CI `npm ci`, `npm run lint`, `npm run typecheck` e `npm run test`.
Primeiro estado vermelho deve ser observado no CI antes dos consertos.

### C2 · Snapshot patrimonial fora do GET (M) — PERF-5

`reports#net_worth` deve ser somente leitura. Criar service/job recorrente no
Solid Queue para gravar o snapshot mensal. Red: duas chamadas ao GET sem alterar
`NetWorthSnapshot.count`; depois, spec do job.

### C3 · Retry e servidor acordando (M) — CONN-2

Configurar no `useApi` timeout e retry exponencial para 502/503/504. Após cerca de
1 segundo sem resposta, informar que o servidor está acordando. Red: 503 seguido
de 200 deve resultar em uma resolução bem-sucedida e tentativas contabilizadas.

## Alta

### A1 · Remover Kira (P) — D1/UX-1

Remover página e todas as referências, atalhos e links órfãos. Validar com build,
typecheck e lint sem referências mortas.

### A2 · Remover React da aplicação Vue (M) — D3/PERF-3/UX-2/UX-3

Manter a timeline em SVG nativo Vue, remover React, ReactDOM, Recharts e plugin
React. Teste de componente deve renderizar duas séries em sequência e refletir a segunda.

### A3 · Paginação de transações por cursor (M) — PERF-1

Cursor `(occurred_on, id)`, índice existente, padrão 50 e carregamento incremental.
Red: 120 transações, 50 na primeira página, continuidade sem repetição nem lacunas.

### A4 · Eliminar N+1 do relatório mensal (P) — PERF-2

Usar agregação por categoria e `index_by` antes do loop. Red: teste de contagem de
queries com teto fixo e 25 categorias.

### A5 · Navegação mobile completa (M) — MOB-1/MOB-2

Quatro itens fixos e folha “Mais” com Relatórios, Importar, Portadores e Configurações.
Reaproveitar Command Palette. Red: toda página autenticada deve ter caminho mobile.

### A6 · Offline e conexão (P) — metade de CONN-1

Tela honesta para ausência de rede e indicador no topbar, sem cachear respostas
financeiras. Red: `navigator.onLine = false` mostra estado offline.

## Média

### M1 · Assumir SPA (P) — D2/PERF-4

Definir `ssr: false`, manter `nuxt build` e verificar CSP nonce no HTML servido.

### M2 · Token curto e fora do JavaScript (G) — SEC-1

Escolher access curto + refresh HttpOnly ou proxy Nitro com cookie HttpOnly. Red:
expiração, rotação e ausência do token em `document.cookie`.

### M3 · Exclusão de conta e exportação (M) — PRIV-1

Adicionar `DELETE /api/v1/users/me` e `GET /api/v1/users/me/export`. Fixar decisão
explícita para `audit_logs`. Red: zero dados residuais após exclusão.

### M4 · Importação assíncrona (M) — PERF-6

Mover parse/dedupe/escrita para Solid Queue, responder 202 com ID e fazer polling.
Checksum incremental por blocos. Red: job fora do request e endpoint rastreável.

### M5 · Rate limit autenticado (P) — SEC-3

Throttle por usuário em rotas autenticadas, mais apertado em imports/reports. Red:
excesso retorna 429 no formato JSON vigente.

### M6 · Fila offline de lançamentos (G) — metade de CONN-1

IndexedDB guarda somente entradas criadas offline, drena ao reconectar e sinaliza
pendências. Red: exatamente um POST no replay, sem duplicata.

## Baixa

### B1 · Sessão por dispositivo (M) — SEC-2

`jti` por sessão em tabela; logout invalida só aquele registro. `token_version`
permanece como botão de pânico na troca de senha. Executar junto do M2.

### B2 · Visita de relatório versus exportação (P) — PRIV-2

`VIEW_REPORT` para abertura de tela e `EXPORT_DATA` somente para download real de
M3. Definir prazo de retenção e expurgo por idade.

### B3 · Atualizar processo e documentação (P)

Reescrever `CLAUDE-process.md` para RSpec, RuboCop, Vitest e o portão C1. Corrigir
Nuxt 4 para Nuxt 3.21 e remover LiteLLM/Kira da stack vigente. Manter legado fora da
fonte de verdade de `apps/` e registrar a decisão no Serena.

## Escala de esforço

`P` ≤ meia sessão · `M` ≈ 1–2 sessões · `G` ≥ 3 sessões ou projeto próprio.

