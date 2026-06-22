# rails-api

Backend central do ecossistema Quebec.

**Stack:** Ruby on Rails 8 + PostgreSQL  
**Status:** Planejado — implementação futura

## Responsabilidades

- Domínio de negócio do Klipper
- API RESTful (`/api/v1/`)
- Autenticação (Devise ou Rails 8 native)
- Jobs assíncronos (Sidekiq ou GoodJob)
- Action Mailer, Action Cable
- Administração interna

## Relação com Supabase

Supabase permanece como provedor de:
- Autenticação do Klipper
- PostgreSQL (banco de dados)
- Storage (uploads)

Rails API consome Supabase e adiciona lógica de domínio.

## Próximos passos

1. `rails new rails-api --api -d postgresql`
2. Configurar autenticação
3. Migrar rotas de `api/` (FastAPI legado)
4. Deprecar `api/` quando cobertura for completa
