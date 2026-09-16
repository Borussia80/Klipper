# CLAUDE.md — Klipper · Contexto de Sessão
> Leia este arquivo PRIMEIRO. Carregue os complementares conforme a tarefa.

---

## IDENTIDADE

**Klipper** — Wealth Operating System pessoal de Roberto Milet.
Stack: **SPA/PWA Nuxt 3.21 (Vercel) + API Rails 8 (PostgreSQL)**
Prod: PWA em Vercel · Repo: https://github.com/Borussia80/Klipper
Local: `/home/rmilet/Base/01-Projetos/11-Klipper`

### Estrutura do monorepo

```
apps/
  klipper-web/    ← Nuxt 3.21 (Vue 3, SPA, PWA) — frontend
  klipper-api/    ← Rails 8 (PostgreSQL, JWT) — backend
  quebec-web/     ← Nuxt 3.21 — landing page institucional
```

---

## ARQUIVOS COMPLEMENTARES — carregue só o necessário

| Se a tarefa envolve… | Carregue |
|---|---|
| Novo arquivo ou novo teste | `CLAUDE-process.md` |
| Nova feature, gap de produto, ou pedido vago sobre o que fazer a seguir | `ROADMAP_KLIPPER_WEALTH_OS.md` |

---

## EXECUÇÃO LOCAL

```bash
# Frontend (Nuxt 3.21, SPA)
cd apps/klipper-web
npm run dev          # localhost:3000
npm run test         # Vitest

# Backend (Rails 8) — requer o Postgres de teste no ar (ver abaixo)
cd apps/klipper-api
TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/klipper_test" \
  bundle exec rspec --format documentation
```

### Postgres de teste — Podman, não Docker

O daemon do Docker está **desabilitado** nesta máquina: `docker compose` falha.
O banco de teste roda como container Podman já criado (`postgres:16`, porta 5432):

```bash
podman start klipper-pg-test
```

Se o container não existir:

```bash
podman run -d --name klipper-pg-test -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres postgres:16
```

Em checkout limpo, rode `npx nuxt prepare` em `apps/klipper-web` antes do Vitest.

---

## REGRA DE OURO DO AGENTE

Matemática ancora. Narrativa sem evidência não altera decisão.
Código sem teste não entra. Não existe "adicionar teste depois".
