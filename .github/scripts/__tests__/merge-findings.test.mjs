// Cobre a deduplicação por natural_key (PIPE-5): o mesmo defeito visto por dois
// agentes tem que reencontrar UM ID permanente, e um ID já comunicado não pode
// virar órfão nem ser reutilizado por um finding novo.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'merge-findings.mjs');

function runMerge({ runFindings, registryFindings, commit = 'aaa111', date = '2026-09-18T00:00:00.000Z' }) {
  const dir = mkdtempSync(path.join(tmpdir(), 'merge-findings-'));
  const runPath = path.join(dir, 'run.json');
  const registryPath = path.join(dir, 'findings.json');
  writeFileSync(runPath, JSON.stringify({
    meta: { date, commit, branch: 'main' },
    findings: runFindings,
  }));
  writeFileSync(registryPath, JSON.stringify({ schema_version: '1.0.0', findings: registryFindings }));
  execFileSync('node', [SCRIPT, runPath, registryPath], { stdio: 'pipe' });
  return {
    registry: JSON.parse(readFileSync(registryPath, 'utf8')),
    run: JSON.parse(readFileSync(runPath, 'utf8')),
  };
}

function finding(overrides = {}) {
  return {
    category: 'finance',
    natural_key: 'some-defect',
    severity: 'medium',
    description: 'descrição',
    recommendation: 'recomendação',
    impact: 5,
    frequency: 5,
    reach: 5,
    effort: 2,
    priority_score: 30,
    adr_candidate: false,
    ...overrides,
  };
}

function registryEntry(overrides = {}) {
  return {
    id: 'FIN-001',
    category: 'finance',
    natural_key: 'some-defect',
    status: 'open',
    component: null,
    adr: null,
    first_seen: { commit: 'old000', branch: 'main', date: '2026-09-01T00:00:00.000Z' },
    last_seen: { commit: 'old000', branch: 'main', date: '2026-09-01T00:00:00.000Z' },
    occurrences: 3,
    severity_history: [{ date: '2026-09-01T00:00:00.000Z', commit: 'old000', severity: 'medium' }],
    ...overrides,
  };
}

test('reencontra o ID permanente mesmo quando o defeito muda de categoria', () => {
  const { registry, run } = runMerge({
    registryFindings: [registryEntry({ id: 'ARCH-003', category: 'architecture' })],
    runFindings: [finding({ category: 'finance' })],
  });

  assert.equal(registry.findings.length, 1, 'não deve criar um segundo ID para a mesma chave');
  assert.equal(registry.findings[0].id, 'ARCH-003');
  assert.equal(run.findings[0].id, 'ARCH-003');
  assert.equal(registry.findings[0].occurrences, 4);
});

test('absorve um par duplicado pré-existente mantendo o ID mais antigo', () => {
  const { registry } = runMerge({
    registryFindings: [
      registryEntry({ id: 'ARCH-003', category: 'architecture', occurrences: 5 }),
      registryEntry({
        id: 'FIN-006',
        category: 'finance',
        occurrences: 2,
        first_seen: { commit: 'new000', branch: 'main', date: '2026-09-10T00:00:00.000Z' },
      }),
    ],
    runFindings: [finding({ category: 'architecture' })],
  });

  assert.equal(registry.findings.length, 1);
  const [entry] = registry.findings;
  assert.equal(entry.id, 'ARCH-003', 'sobrevive o first_seen mais antigo');
  assert.deepEqual(entry.merged_from, ['FIN-006'], 'o ID absorvido fica rastreável');
  assert.equal(entry.occurrences, 6, 'herda a maior contagem (5) e soma a execução atual');
});

test('não reutiliza o número de um ID absorvido num finding novo', () => {
  const { registry } = runMerge({
    registryFindings: [
      registryEntry({ id: 'FIN-005', natural_key: 'defect-a', occurrences: 1 }),
      registryEntry({
        id: 'FIN-006',
        natural_key: 'defect-a',
        occurrences: 1,
        first_seen: { commit: 'new000', branch: 'main', date: '2026-09-10T00:00:00.000Z' },
      }),
    ],
    runFindings: [finding({ natural_key: 'defect-a' }), finding({ natural_key: 'defect-novo' })],
  });

  const ids = registry.findings.map((f) => f.id).sort();
  assert.deepEqual(ids, ['FIN-005', 'FIN-007'], 'FIN-006 foi absorvido e não pode ser reemitido');
});

test('degrada em duas etapas o finding que o run não viu', () => {
  const primeiro = runMerge({
    registryFindings: [registryEntry({ natural_key: 'defect-sumido' })],
    runFindings: [finding({ natural_key: 'outro-defect' })],
  });
  const sumido = primeiro.registry.findings.find((f) => f.natural_key === 'defect-sumido');
  assert.equal(sumido.status, 'not_seen_last_run');

  const segundo = runMerge({
    registryFindings: [primeiro.registry.findings.find((f) => f.natural_key === 'defect-sumido')],
    runFindings: [finding({ natural_key: 'outro-defect' })],
  });
  assert.equal(segundo.registry.findings.find((f) => f.natural_key === 'defect-sumido').status, 'resolved');
});
