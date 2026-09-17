// Cobre o colapso por natural_key (PIPE-5): dois agentes que emitem a mesma
// chave descrevem um defeito só, e o run-report tem que listá-lo uma vez.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'aggregate-report.mjs');

function runAggregate(partials) {
  const dir = mkdtempSync(path.join(tmpdir(), 'aggregate-report-'));
  for (const [i, p] of partials.entries()) {
    writeFileSync(path.join(dir, `partial-${i}.json`), JSON.stringify(p));
  }
  const outputPath = path.join(dir, 'run.json');
  const stdout = execFileSync('node', [SCRIPT, dir, outputPath, '--commit=aaa111', '--branch=main'], {
    encoding: 'utf8',
  });
  return { run: JSON.parse(readFileSync(outputPath, 'utf8')), stdout };
}

function partial(agent, findings, score = 50) {
  return {
    agent,
    section: { name: agent, score, risk: 'medium', findings },
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
    finding_confidence: 'high',
    adr_candidate: false,
    ...overrides,
  };
}

test('colapsa a mesma natural_key vinda de dois agentes num finding só', () => {
  const { run, stdout } = runAggregate([
    partial('architecture', [finding({ category: 'architecture', severity: 'high' })]),
    partial('finance', [finding({ category: 'finance', severity: 'medium' })]),
  ]);

  assert.equal(run.findings.length, 1, 'um defeito, um finding');
  assert.match(stdout, /1 colapsados/);
});

test('sobrevive o de maior severidade e registra quem mais viu', () => {
  const { run } = runAggregate([
    partial('finance', [finding({ category: 'finance', severity: 'medium' })]),
    partial('architecture', [finding({ category: 'architecture', severity: 'high' })]),
  ]);

  const [f] = run.findings;
  assert.equal(f.severity, 'high');
  assert.equal(f.category, 'architecture');
  assert.deepEqual(f.also_reported_by, [{ agent: 'finance', category: 'finance', severity: 'medium' }]);
});

test('empate de severidade decide pelo priority_score maior', () => {
  const { run } = runAggregate([
    partial('finance', [finding({ category: 'finance', effort: 5 })]),
    partial('architecture', [finding({ category: 'architecture', effort: 1 })]),
  ]);

  const [f] = run.findings;
  assert.equal(f.category, 'architecture', 'esforço 1 dá priority_score maior que esforço 5');
  assert.equal(f.priority_score, 125);
});

test('chaves distintas não são colapsadas', () => {
  const { run } = runAggregate([
    partial('finance', [finding({ natural_key: 'defect-a' }), finding({ natural_key: 'defect-b' })]),
    partial('security', [finding({ category: 'security', natural_key: 'defect-c' })]),
  ]);

  assert.equal(run.findings.length, 3);
  assert.equal(run.findings.filter((f) => f.also_reported_by).length, 0);
});

test('três agentes na mesma chave colapsam para um, com dois em also_reported_by', () => {
  const { run } = runAggregate([
    partial('finance', [finding({ category: 'finance', severity: 'low' })]),
    partial('architecture', [finding({ category: 'architecture', severity: 'critical' })]),
    partial('security', [finding({ category: 'security', severity: 'medium' })]),
  ]);

  assert.equal(run.findings.length, 1);
  const [f] = run.findings;
  assert.equal(f.severity, 'critical');
  assert.equal(f.also_reported_by.length, 2);
});
