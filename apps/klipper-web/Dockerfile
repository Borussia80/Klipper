# syntax=docker/dockerfile:1
ARG NODE_VERSION=22-slim
FROM docker.io/library/node:$NODE_VERSION AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# O tracer de dependências do Nitro (node-server preset) às vezes gera um
# node_modules parcial dentro de .output/server — no caso desta build, o
# pacote "vue" ficou como symlink quebrado (só rastreou vue/server-renderer,
# não a entrada principal), e "vue" nem aparece em .output/server/package.json.
# Rodar npm install ali resolve a peer dependency real de @vue/server-renderer
# e substitui o node_modules incompleto por um completo.
RUN rm -rf .output/server/node_modules && cd .output/server && npm install --omit=dev

FROM docker.io/library/node:$NODE_VERSION

# A imagem oficial node:*-slim já vem com um usuário "node" em uid/gid 1000 —
# criar outro aqui colide (GID '1000' already exists) em versões recentes da
# imagem base. Reaproveita o usuário existente em vez de criar um novo.
USER node

WORKDIR /app
COPY --chown=node:node --from=build /app/.output ./.output

ENV PORT=3000
EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
