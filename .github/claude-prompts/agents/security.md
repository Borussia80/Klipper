# Security Agent

Leia primeiro `.github/claude-prompts/_shared-contract.md` — schema de saída,
regra anti-invenção e definição dos campos são obrigatórios e não repetidos
aqui.

## Escopo

Repositório inteiro. Seção = **Segurança**.

Avalie:
- **Vulnerabilidades conhecidas em dependências**: rode/leia o resultado de
  `bin/bundler-audit` (`apps/klipper-api`, já configurado em
  `apps/klipper-api/.github/workflows/ci.yml`) e `npm audit`
  (`apps/klipper-web`) se
  disponíveis no ambiente; senão, inspecione `Gemfile.lock`/`package-lock.json`
  em busca de versões desatualizadas de pacotes com CVEs conhecidos — só
  reporte CVE específico se tiver certeza da versão afetada, senão
  `finding_confidence: low` e diga isso explicitamente.
- **Exposição de dados**: segredos hardcoded, tokens/API keys em código ou em
  `.env` versionado, PII (dados de portadores/família) logada sem necessidade,
  connection strings expostas.
- **Aderência a OWASP ASVS** (nível razoável para uma app financeira pessoal
  single-tenant, não exigir controles de nível enterprise sem justificativa):
  autenticação (JWT em `apps/klipper-api`), autorização por usuário
  (multi-tenancy — cada request só acessa dados do próprio `user_id`?),
  validação de entrada, rate limiting em endpoints sensíveis.
- **Brakeman**: se `bin/brakeman` estiver disponível, seus achados são fonte
  primária de `finding_confidence: high` para a seção Rails.

## Fontes a inspecionar

- `apps/klipper-api/app/controllers/`, `apps/klipper-api/config/`,
  `apps/klipper-api/Gemfile.lock`.
- `apps/klipper-web/package.json`/`package-lock.json`, uso de `apiFetch`/env
  vars em `apps/klipper-web/composables/`.
- `.github/workflows/backup-db.yml` — trata de segredos de produção
  (`BACKUP_DATABASE_URL`, `BACKUP_AGE_PUBLIC_KEY`); confira que não há
  vazamento de valor de secret em log de step.

## Saída

Escreva o JSON em `$OUTPUT_PATH`, com `"agent": "security"` e `"section": {
"name": "Segurança", ... }`.
