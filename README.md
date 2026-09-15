# Klipper — Wealth Operating System

Sistema pessoal de gestão financeira e patrimonial. Matemática ancora. Narrativa sem
evidência não altera decisão. Código sem teste não entra.

**Stack:** Nuxt 3.21 (Vue 3, SPA/PWA) · Rails 8 (PostgreSQL, JWT) · Vercel · Render · Neon

**Produção:** https://klipper.quebec.com.br · **Repo:** https://github.com/Borussia80/Klipper

---

## Monorepo

```
apps/
  klipper-web/    ← Nuxt 3.21 — frontend (dashboard, transações, orçamento, investimentos, import)
  klipper-api/    ← Rails 8 — backend (API JSON, JWT, PostgreSQL)
  quebec-web/     ← Nuxt 3.21 — landing page institucional
```

Cada app tem seu próprio `package.json`/`Gemfile` e roda independente.

---

## Executar localmente

### Opção 1 — cada app na mão (dia a dia de desenvolvimento)

```bash
# Backend — requer o Postgres local no ar.
# O daemon do Docker está desabilitado nesta máquina; o banco roda em Podman:
podman start klipper-pg-test   # ou, se não existir:
# podman run -d --name klipper-pg-test -p 5432:5432 \
#   -e POSTGRES_PASSWORD=postgres postgres:16
cd apps/klipper-api
bin/rails db:prepare
bin/rails server -p 3001

# Frontend, em outro terminal
cd apps/klipper-web
npm install
npm run dev          # http://localhost:3000
```

### Opção 2 — stack completa via Docker Compose (perfil "local pessoal")

Sobe Postgres + API + Web + proxy Caddy isolados na rede Docker, só acessível em
`127.0.0.1:8080` — pensado pra guardar dado financeiro real localmente, sem expor
serviço nenhum além do proxy.

> Esta opção depende de um daemon Docker funcionando, que **não é o caso da máquina
> de desenvolvimento atual** (ver Opção 1). Rodar com `podman-compose` é plausível mas
> não foi testado — trate o comando abaixo como não verificado.

```bash
cp .env.local.example .env.local   # preencher POSTGRES_PASSWORD e RAILS_MASTER_KEY
docker compose --env-file .env.local -f docker-compose.local.yml up -d --build
```

---

## Testes

```bash
# Backend (RSpec)
cd apps/klipper-api
TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/klipper_test" \
  bundle exec rspec --format documentation

# Frontend (Vitest)
cd apps/klipper-web
npm run test
```

TDD é obrigação técnica neste repo — ver `CLAUDE-process.md` (ciclo Red → Green →
Refactor, F.I.R.S.T., SRP). Código sem teste correspondente não entra.

---

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) roda em todo push/PR: Brakeman + Bundler
Audit (segurança Ruby) → RuboCop (lint) → RSpec (backend). Deploy é automático a partir
de merge em `main`:

- **Frontend** (`klipper-web`, `quebec-web`) → Vercel, `target: production`
- **Backend** (`klipper-api`) → Render (`apps/klipper-api/render.yaml`), Postgres em Neon

`klipper-api` está no plano Free do Render — a primeira requisição após um período de
inatividade sofre cold start (~30s). Migrations rodam via `bin/docker-entrypoint` a cada
boot do container, não via `render.yaml`/`preDeployCommand` (o Render Free ignora esse
hook — só roda em planos pagos).

---

## Documentação

| O quê | Onde |
|---|---|
| Contexto de sessão / arquitetura | `CLAUDE.md` |
| Processo de desenvolvimento (TDD, F.I.R.S.T., SRP) | `CLAUDE-process.md` |
| Roadmap de produto + backlog de segurança | `ROADMAP_KLIPPER_WEALTH_OS.md` |
| Plano de execução da auditoria de 14/09/2026 | `PLANO_EXECUCAO_KLIPPER_2026-09-14.md` |
| Feature Kakebo — especificação do ciclo mensal | `docs/KAKEBO.md` |
| Auditorias de segurança | `docs/security/` |
| ADRs | `docs/adrs/` |
| Runbook de erros de operação/deploy | `docs/operations/matriz-erros.md` |

---

## Regra de ouro

Matemática ancora. Narrativa sem evidência não altera decisão. Código sem teste não
entra. Não existe "adicionar teste depois".
