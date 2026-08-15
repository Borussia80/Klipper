# Matriz de Erros — Diagnóstico Rápido (Klipper)

Guia vivo de triagem: sintoma visível → o que olhar no DevTools → causa provável →
correção. Não é uma lista genérica de status HTTP — cada linha vem de um incidente
real neste projeto, ou de um caminho de código já verificado que produziria o
sintoma descrito.

## Como usar

1. Abrir DevTools → aba **Network** no momento do erro (deixar aberto antes de
   reproduzir, senão perde a requisição).
2. Achar a chamada pra API (`/api/v1/...`).
3. Ver o **Status** da requisição (ou se ela nem aparece / aparece como `(failed)`)
   e comparar contra a tabela abaixo.
4. Se nenhuma linha bater, checar o Console em paralelo (erros de CORS aparecem lá,
   não na aba Network com status code).

## Tabela

| Sintoma na tela | Network tab mostra | Causa provável | Onde checar / corrigir |
|---|---|---|---|
| Mensagem genérica ("Não foi possível criar a conta.", "Não foi possível fazer login.") sem detalhe | Requisição não aparece com status, ou aparece como `(failed)` / erro de CORS no Console | `CORS_ORIGINS` do backend não inclui o domínio atual do frontend — o browser bloqueia antes da API responder | `apps/klipper-api/config/initializers/cors.rb:3` + env `CORS_ORIGINS` no Render (dashboard `klipper-api` → Environment) |
| Mesma mensagem genérica, mas a requisição aparece com status 4xx/5xx real | Status visível (422/401/403/429/500) | Não é CORS — é um erro real sendo mascarado pelo fallback do frontend, que só mostra a mensagem específica se `e.data` vier preenchido | `apps/klipper-web/pages/login.vue:160-162` — ver a linha certa abaixo pelo status |
| Cadastro rejeitado mesmo com dados aparentemente válidos | Status 422, corpo `{ "errors": [...] }` | Validação de `User` falhou: e-mail já cadastrado, formato de e-mail inválido, ou senha com menos de 8 caracteres | `apps/klipper-api/app/models/user.rb:15-16` |
| "Muitas tentativas..." ou bloqueio temporário em login/cadastro | Status 429 | Throttle do Rack::Attack — 20 req/min por IP em sign_in/sign_up/password_resets, 5/min por e-mail em sign_in | `apps/klipper-api/config/initializers/rack_attack.rb` |
| 403 em qualquer rota da API, corpo simples (não é JSON de validação) | Status 403 | `RAILS_ALLOWED_HOSTS` configurado no Render com um hostname que não bate com o `Host` real da requisição — protege a própria API, não o domínio do frontend | `config.hosts` em `apps/klipper-api/config/environments/production.rb` + `RAILS_ALLOWED_HOSTS` no Render |
| Botão/tela chama a API e recebe 404 | Status 404 | Rota não implementada no backend (frontend chamando um endpoint que nunca existiu — já aconteceu com `/api/v1/kira/chat`) | `apps/klipper-api/config/routes.rb` — se for feature ainda não implementada, desconectar do frontend até ter backend |
| Tela branca / erro genérico em produção, mas funciona local (`npm run dev`) | Function da Vercel retorna 500; log da função mostra `ERR_MODULE_NOT_FOUND` | Dependência duplicada/órfã no lockfile — o npm não deduplicou, e o build do Nitro empacotou a versão errada na Function | Rodar `NITRO_PRESET=vercel npm run build` local (reproduz o build exato da Vercel) e conferir `.vercel/output/functions/.../node_modules` |

## Casos resolvidos (histórico)

- **2026-08-15** — `CORS_ORIGINS` desatualizado após configurar o domínio custom
  (`klipper.quebec.com.br`) sem atualizar a allowlist do backend, que só liberava
  `klipper-app.vercel.app`. Bloqueava cadastro e login em produção com mensagem
  genérica. Corrigido em `apps/klipper-api/render.yaml`.
- **2026-08-15** — `ERR_MODULE_NOT_FOUND: vue/index.mjs` em produção — dependência
  `vue` duplicada no lockfile (versão órfã não satisfazia o range pedido por
  `nuxt`/`@nuxt/nitro-server`), Nitro empacotou a versão errada na Function.
  Corrigido com `overrides` em `apps/klipper-web/package.json` (commit `5e8041d`).

## Adicionando uma nova linha

Só entra na tabela um sintoma que já foi observado de verdade (produção ou
reprodução local) e cuja causa foi confirmada lendo o código-fonte ou os logs —
não hipóteses. Ao fechar um incidente novo, adicionar a linha na tabela E uma
entrada no histórico com a data.
