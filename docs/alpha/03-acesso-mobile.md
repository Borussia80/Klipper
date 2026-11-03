# Acesso pelo celular (PWA)

O Klipper é um PWA: não há app de loja. O celular instala o próprio site
publicado em HTTPS.

## Por que o front encaminha a API

O refresh token é um cookie `HttpOnly`, `SameSite=Lax`, com `Path=/api/v1/auth`.
Se o front estiver em `*.vercel.app` e a API em `*.onrender.com`, os dois estão em
sites diferentes e o navegador não envia esse cookie nas chamadas `fetch`. O
login funciona, mas a sessão cai quando o token de acesso expira (15 min).

Com `KLIPPER_API_PROXY_TARGET` definido no build, o Nitro encaminha `/api/**` à
API e o navegador só fala com a origem do front (ver
`apps/klipper-web/config/apiRouting.ts`). O cookie passa a ser da origem do front
e é enviado normalmente.

## Configuração

Vercel (projeto com root em `apps/klipper-web`):

| Variável | Valor |
|---|---|
| `KLIPPER_API_PROXY_TARGET` | URL da API, por exemplo `https://klipper-api.onrender.com` (exige `https`) |
| `NUXT_PUBLIC_API_URL` | **Não definir.** Se definida, sobrepõe a mesma origem em tempo de execução e volta o problema do cookie. |

A variável é lida no build: depois de alterá-la, faça um novo deploy.

Render (API): `RAILS_ALLOWED_HOSTS` precisa conter o host da própria API
(`klipper-api.onrender.com`), porque o proxy envia esse `Host`. O `CORS_ORIGINS`
deixa de ser usado pelo front, que agora faz chamadas de mesma origem.

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
