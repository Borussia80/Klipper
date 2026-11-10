# Acesso pelo celular (PWA)

O Klipper é um PWA: não há app de loja. O celular instala o próprio site
publicado em HTTPS.

## Por que o front encaminha a API

O refresh token é um cookie `HttpOnly`, `SameSite=Lax`, com `Path=/api/v1/auth`.
Se o front estiver em `*.vercel.app` e a API em `*.onrender.com`, os dois estão em
sites diferentes e o navegador não envia esse cookie nas chamadas `fetch`. O
login funciona, mas a sessão cai quando o token de acesso expira (15 min).

No build da Vercel, o Nitro encaminha `/api/**` à API e o navegador só fala
com a origem do front (ver `apps/klipper-web/config/apiRouting.ts`). O cookie
passa a ser da origem do front e é enviado normalmente.

## Configuração

Vercel (projeto com root em `apps/klipper-web`): nada novo. O destino do
repasse é o `NUXT_PUBLIC_API_URL` que já existe no projeto
(`https://klipper-api.onrender.com`, em Production). Ele só é lido no build;
depois de alterá-lo, faça um novo deploy.

| Variável | Uso |
|---|---|
| `NUXT_PUBLIC_API_URL` | Num build da Vercel, se for `https`, vira o destino do repasse. Fora da Vercel, continua sendo a URL chamada direto pelo navegador. |
| `KLIPPER_API_PROXY_TARGET` | Opcional. Força o destino do repasse em qualquer ambiente (exige `https`, exceto `localhost`). |
| `NUXT_PUBLIC_API_BASE` | Sobrepõe em tempo de execução a base usada pelo navegador. Na Vercel, **não definir**: anularia a mesma origem. O perfil Docker usa `""`. |

O preview dos PRs não tem `NUXT_PUBLIC_API_URL` e continua sem API, como antes.

Render (API): `RAILS_ALLOWED_HOSTS` precisa conter `klipper-api.onrender.com`,
`klipper.quebec.com.br`, `www.klipper.quebec.com.br` e
`klipper-app.vercel.app`. O proxy Nitro envia o host do front em
`X-Forwarded-Host`, que o HostAuthorization do Rails valida. Se os domínios do
front faltarem, POSTs pelo proxy retornam 403 com corpo vazio, embora
`/api/v1/health` responda 200 (rota excluída dessa validação). O `CORS_ORIGINS`
deixa de ser usado pelo front, que agora faz chamadas de mesma origem.

Diagnóstico: se a API aparece como `Live`, mas não responde, confira o log de
boot do Render, especialmente falhas em `db:prepare` por `DATABASE_URL` inválida
ou desatualizada.

## Limitação conhecida

Com o proxy, a API vê o IP de saída da Vercel, não o do aparelho. O limite do
Rack::Attack por IP (20 tentativas de login/cadastro por minuto) passa a ser
compartilhado entre todos os usuários. Para uso pessoal não é um problema. O
limite por e-mail continua valendo. Antes de abrir para mais participantes,
reavaliar isso.

## Instalar no celular

- Android (Chrome): abrir o endereço do front, menu ⋮ e depois "Instalar app".
- iPhone (Safari): abrir o endereço, Compartilhar e depois "Adicionar à Tela de Início".

Os ícones ficam em `apps/klipper-web/public/icons/`. Um teste confere se cada
arquivo tem as dimensões declaradas no manifest.
