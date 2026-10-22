#!/usr/bin/env bash
# Backup semanal do Postgres local do Klipper (container `db` do
# docker-compose.local.yml, rodando em Podman no servidor).
# Gera um dump no formato custom, cifra com age e poda os antigos.
#
# Variáveis (normalmente vindas de ~/.config/klipper-backup.env):
#   BACKUP_DIR     pasta de destino (ex.: o HD externo)            [obrigatória]
#   AGE_RECIPIENT  chave PÚBLICA age (age1...)                      [obrigatória]
#   CONTAINER      nome do container do Postgres (descobre sozinho se vazio)
#   KEEP_WEEKS     semanas de retenção (padrão 12)
set -euo pipefail

: "${BACKUP_DIR:?defina BACKUP_DIR}"
: "${AGE_RECIPIENT:?defina AGE_RECIPIENT (chave pública age1...)}"
KEEP_WEEKS="${KEEP_WEEKS:-12}"
PODMAN="${PODMAN:-podman}"

CONTAINER="${CONTAINER:-}"
if [ -z "$CONTAINER" ]; then
  for label in com.docker.compose.service io.podman.compose.service; do
    CONTAINER=$("$PODMAN" ps --filter "label=${label}=db" --format '{{.Names}}' | head -n1)
    [ -n "$CONTAINER" ] && break
  done
fi
if [ -z "$CONTAINER" ]; then
  echo "Container do Postgres não encontrado. Ele está rodando? Defina CONTAINER=<nome>." >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"
TS=$(date -u +%Y%m%d-%H%M%S)
OUT="$BACKUP_DIR/klipper_${TS}.pgdump.age"
TMP="${OUT}.partial"
trap 'rm -f "$TMP"' EXIT

# pipefail: se o pg_dump falhar, o script falha e nenhum arquivo parcial vira backup.
"$PODMAN" exec "$CONTAINER" pg_dump -U klipper -d klipper_local --format=custom \
  | age --encrypt --recipient "$AGE_RECIPIENT" --output "$TMP"

if [ ! -s "$TMP" ]; then
  echo "Backup vazio — abortando." >&2
  exit 1
fi
mv "$TMP" "$OUT"
echo "Backup gravado: $OUT"

find "$BACKUP_DIR" -maxdepth 1 -name 'klipper_*.pgdump.age' -mtime "+$((KEEP_WEEKS * 7))" \
  -print -delete | sed 's/^/Removido (expirado): /'
