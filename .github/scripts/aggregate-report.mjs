#!/usr/bin/env node
// Consolida N partial-<agent>.json (já validados por validate-partial.mjs)
// num único run-report.json: score geral, Priorização RICE (usando
// finding_confidence, não model_confidence) e Possible Regressions
// (comparação contra reports/registry/findings.json, se fornecido).
// Roda ANTES de merge-findings.mjs — findings ainda não têm ID permanente,
// são casados por (category, natural_key).
import { readdirSync } from 'node:fs';
import path from 'node:path';
import { readJson, writeJson, parseArgs, fail } from './lib.mjs';

const CONFIDENCE_MULTIPLIER = { high: 1.0, medium: 0.6, low: 0.3 };
const SEVERITY_RANK = { critical: 4, high: 3, medium: 2, low: 1 };

const args = parseArgs(process.argv.slice(2));
const partialsDir = args._[0];
const outputPath = args._[1];
if (!partialsDir || !outputPath) {
  fail('uso: aggregate-report.mjs <partials-dir> <output.json> [--depth=fast|deep] [--trigger=...] [--branch=...] [--commit=...] [--registry=reports/registry/findings.json]');
}

const files = readdirSync(partialsDir).filter((f) => f.startsWith('partial-') && f.endsWith('.json'));
if (files.length === 0) fail(`nenhum partial-*.json encontrado em ${partialsDir}`);

const sections = [];
const findings = [];

for (const file of files) {
  const data = readJson(path.join(partialsDir, file));
  sections.push({ agent: data.agent, name: data.section.name, score: data.section.score, risk: data.section.risk });
  for (const f of data.section.findings) {
    const multiplier = CONFIDENCE_MULTIPLIER[f.finding_confidence] ?? 0;
    const priority_score = multiplier === 0 ? 0 : Math.round(((f.impact * f.frequency * f.reach * multiplier) / f.effort) * 100) / 100;
    findings.push({ ...f, agent: data.agent, priority_score });
  }
}

findings.sort((a, b) => b.priority_score - a.priority_score);

const overall_score = sections.length
  ? Math.round((sections.reduce((sum, s) => sum + s.score, 0) / sections.length) * 100) / 100
  : 0;

let possible_regressions = [];
if (args.registry) {
  const registry = readJson(args.registry);
  const byKey = new Map(registry.findings.map((f) => [`${f.category}::${f.natural_key}`, f]));
  for (const f of findings) {
    const prior = byKey.get(`${f.category}::${f.natural_key}`);
    if (!prior || !prior.severity_history || prior.severity_history.length === 0) continue;
    const lastSeverity = prior.severity_history[prior.severity_history.length - 1].severity;
    if (SEVERITY_RANK[f.severity] > SEVERITY_RANK[lastSeverity]) {
      possible_regressions.push({
        id: prior.id,
        natural_key: f.natural_key,
        category: f.category,
        previous_severity: lastSeverity,
        current_severity: f.severity,
        evidence: f.evidence,
      });
    }
  }
}

const run = {
  schema_version: '1.0.0',
  meta: {
    date: new Date().toISOString(),
    trigger: args.trigger ?? 'unknown',
    depth: args.depth ?? (sections.length >= 5 ? 'deep' : 'fast'),
    branch: args.branch ?? 'unknown',
    commit: args.commit ?? 'unknown',
  },
  overall_score,
  sections,
  findings,
  possible_regressions,
};

writeJson(outputPath, run);
console.log(
  `run-report gravado em ${outputPath}: ${sections.length} seções, ${findings.length} findings, ` +
    `${possible_regressions.length} possible regressions, overall_score=${overall_score}`
);
