# syntax=docker/dockerfile:1
ARG NODE_VERSION=22-slim
FROM docker.io/library/node:$NODE_VERSION AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM docker.io/library/node:$NODE_VERSION

RUN groupadd --system --gid 1000 nuxt && \
    useradd nuxt --uid 1000 --gid 1000 --create-home --shell /bin/bash
USER 1000:1000

WORKDIR /app
COPY --chown=nuxt:nuxt --from=build /app/.output ./.output

ENV PORT=3000
EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
