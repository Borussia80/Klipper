# Runtime Agent

Leia primeiro `.github/claude-prompts/_shared-contract.md` — schema de saída,
regra anti-invenção e definição dos campos são obrigatórios e não repetidos
aqui.

## Escopo

Repositório inteiro. Seção = **Performance + Confiabilidade operacional**
(as duas foram deliberadamente combinadas num agente só, por decisão
explícita do usuário — são "outra categoria" frente a código estático, ambas
dependem de observação de comportamento/infra, não só leitura de diff).

Avalie:
- **Performance**: consultas N+1 óbvias em `apps/klipper-api` (`includes`
  ausente onde há loop sobre associação), ausência de índice em coluna usada
  em `WHERE`/`JOIN` frequente (ver `db/schema.rb`), bundle size ou
  chamadas de API redundantes no frontend (ex: `useMemberSpending.ts` já cria
  uma instância de `useReports()` por iteração de `Promise.all` — confirme se
  isso ainda é seguro, ver contexto em memória do projeto sobre esse padrão).
  **Você não tem acesso a métricas reais de produção (latência, uso de
  memória) neste ambiente de CI** — se não houver uma fonte real (ex: log de
  CI, resultado de teste de carga versionado), escreva `Evidence
  unavailable.` em vez de estimar número de latência.
- **Confiabilidade operacional**: `.github/workflows/backup-db.yml` (backup
  semanal, retenção de 12 semanas) está de fato configurado e não quebrado;
  observabilidade (há algum log estruturado, ou é só `Rails.logger` default?);
  SLOs — não existem SLOs formais hoje, reporte isso como gap em vez de
  inventar um; incidentes recentes — só liste se houver evidência real (ex:
  entrada de roadmap ou memória do projeto mencionando um incidente), nunca
  invente.

## Saída

Escreva o JSON em `$OUTPUT_PATH`, com `"agent": "runtime"` e um único
`"section"` cujo `"name"` deve indicar as duas frentes, ex: `"Performance &
Confiabilidade operacional"`. Se quiser diferenciar findings de Performance
vs. Confiabilidade dentro da mesma seção, use o campo `category` do finding
(`"runtime"` para ambos é aceitável — a distinção fica na `description`).
