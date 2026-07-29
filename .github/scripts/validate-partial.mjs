#!/usr/bin/env node
// Valida um partial-<agent>.json contra o schema de _shared-contract.md
// antes de deixar aggregate-report.mjs consumi-lo. Sai com status != 0
// (derrubando o job) se o schema não bater — melhor falhar aqui do que
// corromper reports/registry/findings.json com um formato inválido.
import { readJson, fail } from './lib.mjs';

const SEVERITIES = ['critical', 'high', 'medium', 'low'];
const CONFIDENCES = ['high', 'medium', 'low'];
const AGENTS = ['architecture', 'security', 'finance', 'runtime', 'ux'];
const NATURAL_KEY_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;

const filePath = process.argv[2];
if (!filePath) fail('uso: validate-partial.mjs <path-to-partial.json>');

const data = readJson(filePath);

function assert(cond, msg) {
  if (!cond) fail(`${filePath}: ${msg}`);
}

assert(data.schema_version === '1.0.0', 'schema_version ausente ou não suportado');
assert(AGENTS.includes(data.agent), `agent inválido: ${data.agent}`);
assert(data.section && typeof data.section === 'object', 'section ausente');
assert(typeof data.section.name === 'string' && data.section.name.length > 0, 'section.name ausente');
assert(
  Number.isFinite(data.section.score) && data.section.score >= 0 && data.section.score <= 100,
  'section.score deve ser um número entre 0 e 100'
);
assert(SEVERITIES.includes(data.section.risk), `section.risk inválido: ${data.section.risk}`);
assert(Array.isArray(data.section.findings), 'section.findings deve ser array');

data.section.findings.forEach((f, i) => {
  const where = `section.findings[${i}]`;
  assert(typeof f.natural_key === 'string' && NATURAL_KEY_RE.test(f.natural_key), `${where}.natural_key deve ser kebab-case`);
  assert(typeof f.category === 'string' && f.category.length > 0, `${where}.category ausente`);
  assert(SEVERITIES.includes(f.severity), `${where}.severity inválido: ${f.severity}`);
  assert(CONFIDENCES.includes(f.model_confidence), `${where}.model_confidence inválido: ${f.model_confidence}`);
  assert(CONFIDENCES.includes(f.finding_confidence), `${where}.finding_confidence inválido: ${f.finding_confidence}`);
  assert(typeof f.evidence === 'string' && f.evidence.length > 0, `${where}.evidence ausente`);
  assert(typeof f.description === 'string' && f.description.length > 0, `${where}.description ausente`);
  assert(typeof f.recommendation === 'string' && f.recommendation.length > 0, `${where}.recommendation ausente`);
  for (const field of ['impact', 'frequency', 'reach', 'effort']) {
    assert(Number.isInteger(f[field]) && f[field] >= 1 && f[field] <= 10, `${where}.${field} deve ser inteiro entre 1 e 10`);
  }
  assert(typeof f.adr_candidate === 'boolean', `${where}.adr_candidate deve ser boolean`);
});

console.log(`OK: ${filePath} válido (${data.section.findings.length} findings, agent=${data.agent})`);
