#!/usr/bin/env bash
# Teste do klipper-backup.sh com podman e age de mentira (sem banco real).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/bin" "$T/out"

cat > "$T/bin/podman" <<'STUB'
#!/usr/bin/env bash
case "$1" in
  ps)   [ "${FAKE_NO_CONTAINER:-}" = 1 ] || echo "klipper_db_1" ;;
  exec) [ "${FAKE_DUMP_FAIL:-}" = 1 ] && exit 1; echo "dados-do-dump" ;;
esac
STUB
cat > "$T/bin/age" <<'STUB'
#!/usr/bin/env bash
while [ $# -gt 0 ]; do [ "$1" = "--output" ] && out="$2"; shift; done
{ echo "cifrado:"; cat; } > "$out"
STUB
chmod +x "$T/bin/podman" "$T/bin/age"
export PATH="$T/bin:$PATH" BACKUP_DIR="$T/out" AGE_RECIPIENT="age1teste"
fail() { echo "FALHOU: $1" >&2; exit 1; }

# 1) caminho feliz
"$HERE/klipper-backup.sh" >/dev/null
[ "$(ls "$T/out"/klipper_*.pgdump.age | wc -l)" = 1 ] || fail "deveria gerar 1 backup"
grep -q "dados-do-dump" "$T/out"/klipper_*.pgdump.age || fail "conteúdo do dump ausente"

# 2) poda: arquivo com 100 dias some, o novo fica
touch -d '100 days ago' "$T/out/klipper_antigo.pgdump.age"
"$HERE/klipper-backup.sh" >/dev/null
[ ! -e "$T/out/klipper_antigo.pgdump.age" ] || fail "backup expirado não foi podado"

# 3) pg_dump falhando não deixa backup novo nem parcial
N=$(ls "$T/out" | wc -l)
FAKE_DUMP_FAIL=1 "$HERE/klipper-backup.sh" >/dev/null 2>&1 && fail "deveria falhar quando o pg_dump falha"
[ "$(ls "$T/out" | wc -l)" = "$N" ] || fail "sobrou arquivo após falha do dump"

# 4) sem container
FAKE_NO_CONTAINER=1 "$HERE/klipper-backup.sh" >/dev/null 2>&1 && fail "deveria falhar sem container"

# 5) sem chave
env -u AGE_RECIPIENT "$HERE/klipper-backup.sh" >/dev/null 2>&1 && fail "deveria exigir AGE_RECIPIENT"
echo "OK: 5 cenários"
