#!/usr/bin/env bash
set -euo pipefail
umask 077

: "${DATABASE_URL:?BACKUP_DATABASE_URL não configurada}"
: "${AGE_RECIPIENT:?BACKUP_AGE_PUBLIC_KEY não configurada}"
: "${BACKUP_OUTPUT:?Destino do backup não configurado}"

if [[ -e "$BACKUP_OUTPUT" ]]; then
  echo 'O arquivo de backup já existe; não será sobrescrito.' >&2
  exit 1
fi

# O dump é cifrado no fluxo: não há arquivo temporário em texto puro no runner.
temp_dir=$(mktemp -d "${BACKUP_OUTPUT}.partial.XXXXXX")
trap 'rm -rf -- "$temp_dir"' EXIT
pg_dump "$DATABASE_URL" --format=custom | age --encrypt --recipient "$AGE_RECIPIENT" --output "$temp_dir/backup.age"
test -s "$temp_dir/backup.age"
# Link atômico no mesmo filesystem impede sobrescrever um destino existente.
ln -- "$temp_dir/backup.age" "$BACKUP_OUTPUT"
