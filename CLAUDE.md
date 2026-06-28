# CLAUDE.md — Klipper · Contexto de Sessão
> Leia este arquivo PRIMEIRO. Carregue os complementares conforme a tarefa.

---

## IDENTIDADE

**Klipper** — Wealth Operating System pessoal de Roberto Milet.
Stack: **PWA Nuxt 4 (Vercel) + API Rails 8 (PostgreSQL)** · LiteLLM
Prod: PWA em Vercel · Repo: https://github.com/Borussia80/Klipper
Local: `/home/rmilet/Base/01-Projetos/11-Klipper/Klipper`

### Estrutura do monorepo

```
apps/
  klipper-web/    ← Nuxt 4 (Vue 3, SSR, PWA) — frontend
  klipper-api/    ← Rails 8 (PostgreSQL, JWT) — backend
  quebec-web/     ← Nuxt 4 — landing page institucional
```

> **Stacks removidas:** Streamlit, Next.js, FastAPI, Railway.
> Não existem mais: `app.py`, `pages/`, `web/`, `api/`, `core/`, `models/`.

---

## ARQUIVOS COMPLEMENTARES — carregue só o necessário

| Se a tarefa envolve… | Carregue |
|---|---|
| Novo arquivo ou novo teste | `CLAUDE-process.md` |

---

## EXECUÇÃO LOCAL

```bash
# Frontend (Nuxt 4)
cd apps/klipper-web
npm run dev          # localhost:3000
npm run test         # Vitest

# Backend (Rails 8) — requer Docker Postgres
cd apps/klipper-api
TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/klipper_test" \
  bundle exec rspec --format documentation
```

### Docker Postgres (para testes Rails)
```bash
cd apps/klipper-api
sudo docker compose up -d db
```

---

## REGRA DE OURO DO AGENTE

Matemática ancora. Narrativa sem evidência não altera decisão.
Código sem teste não entra. Não existe "adicionar teste depois".
