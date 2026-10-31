import { test } from 'node:test'
import assert from 'node:assert/strict'
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, readdirSync, rmSync, chmodSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { spawnSync } from 'node:child_process'

test('backup cifrado valida configuração e não deixa arquivos parciais', async t => {
  const temp = mkdtempSync(join(tmpdir(), 'klipper-backup-test-'))
  const bin = join(temp, 'bin')
  const output = join(temp, 'backup.pgdump.age')
  mkdirSync(bin)
  const makeStub = (name, source) => {
    const path = join(bin, name)
    writeFileSync(path, source)
    chmodSync(path, 0o755)
  }
  makeStub('pg_dump', '#!/usr/bin/env bash\n[ "${FAIL_DUMP:-}" != 1 ] || exit 1\nprintf "dump-sintetico"\n')
  makeStub('age', '#!/usr/bin/env bash\nwhile [ "$#" -gt 0 ]; do if [ "$1" = "--output" ]; then out="$2"; shift; fi; shift; done\ncat > "$out"\n[ "${FAIL_AGE:-}" != 1 ]\n')
  const run = extra => spawnSync('bash', [resolve('scripts/backup/create-encrypted-backup.sh')], {
    encoding: 'utf8',
    env: { ...process.env, PATH: `${bin}:${process.env.PATH}`, DATABASE_URL: 'postgresql://example/test', AGE_RECIPIENT: 'age1example', BACKUP_OUTPUT: output, ...extra },
  })

  try {
    await t.test('recusa banco ou destinatário ausente antes de gerar arquivo', () => {
      for (const empty of [{ DATABASE_URL: '' }, { AGE_RECIPIENT: '' }, { BACKUP_OUTPUT: '' }]) {
        assert.notEqual(run(empty).status, 0)
        assert.deepEqual(readdirSync(temp).sort(), ['bin'])
      }
    })
    await t.test('falha no dump ou na cifragem não publica arquivo nem deixa parcial', () => {
      for (const failure of [{ FAIL_DUMP: '1' }, { FAIL_AGE: '1' }]) {
        assert.notEqual(run(failure).status, 0)
        assert.deepEqual(readdirSync(temp).sort(), ['bin'])
      }
    })
    await t.test('publica o resultado cifrado após sucesso', () => {
      assert.equal(run({}).status, 0)
      assert.equal(readFileSync(output, 'utf8'), 'dump-sintetico')
      assert.deepEqual(readdirSync(temp).sort(), ['backup.pgdump.age', 'bin'])
      rmSync(output)
    })
    await t.test('não sobrescreve uma cópia existente', () => {
      writeFileSync(output, 'backup-anterior')
      assert.notEqual(run({}).status, 0)
      assert.equal(readFileSync(output, 'utf8'), 'backup-anterior')
    })
  } finally {
    rmSync(temp, { recursive: true, force: true })
  }
})

test('workflow agenda backup diário e não remove cópias existentes', () => {
  const workflow = readFileSync('.github/workflows/backup-db.yml', 'utf8')
  assert.match(workflow, /cron:\s*['"]0 3 \* \* \*['"]/)
  assert.doesNotMatch(workflow, /gh release delete/)
  assert.match(workflow, /scripts\/backup\/create-encrypted-backup\.sh/)
})
