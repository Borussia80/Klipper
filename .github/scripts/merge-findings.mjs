#!/usr/bin/env node
// Casa os findings do run-report.json contra reports/registry/findings.json
// por (category, natural_key), atribui/preserva o ID permanente
// (ex: ARCH-018), e atualiza first_seen/last_seen/occurrences/
// severity_history. Findings do registry não vistos nesta execução
// degradam de status em duas etapas (open -> not_seen_last_run ->
// resolved) em vez de sumir ou "resolver" de imediato — isso evita que uma
// falha pontual de um agente apague histórico de dívida real.
import { readJson, writeJson, parseArgs, fail } from './lib.mjs';

const PREFIX = {
  architecture: 'ARCH',
  security: 'SEC',
  finance: 'FIN',
  runtime: 'RUN',
  ux: 'UX',
};

const args = parseArgs(process.argv.slice(2));
const runPath = args._[0];
const registryPath = args._[1];
const outRunPath = args.out ?? runPath;
if (!runPath || !registryPath) {
  fail('uso: merge-findings.mjs <run-report.json> <registry/findings.json> [--out=<path>]');
}

const run = readJson(runPath);
const registry = readJson(registryPath);
const { date, commit, branch } = run.meta;

const nextSeq = {};
for (const f of registry.findings) {
  const [prefix, seqStr] = f.id.split('-');
  nextSeq[prefix] = Math.max(nextSeq[prefix] ?? 0, Number(seqStr));
}

const byKey = new Map(registry.findings.map((f) => [`${f.category}::${f.natural_key}`, f]));
const seenKeys = new Set();

for (const finding of run.findings) {
  const key = `${finding.category}::${finding.natural_key}`;
  seenKeys.add(key);
  let entry = byKey.get(key);

  if (!entry) {
    const prefix = PREFIX[finding.category] ?? finding.category.slice(0, 3).toUpperCase();
    nextSeq[prefix] = (nextSeq[prefix] ?? 0) + 1;
    entry = {
      id: `${prefix}-${String(nextSeq[prefix]).padStart(3, '0')}`,
      category: finding.category,
      natural_key: finding.natural_key,
      status: 'open',
      component: null,
      adr: null,
      first_seen: { commit, branch, date },
      last_seen: { commit, branch, date },
      occurrences: 0,
      severity_history: [],
    };
    registry.findings.push(entry);
    byKey.set(key, entry);
  }

  entry.status = 'open';
  entry.last_seen = { commit, branch, date };
  entry.occurrences += 1;
  entry.severity_history.push({ date, commit, severity: finding.severity });
  // Última descrição/recomendação/prioridade conhecidas — necessário para
  // render-report.mjs conseguir listar findings no debt-register mesmo em
  // execuções onde o agente correspondente não rodou (modo Fast, por ex).
  entry.description = finding.description;
  entry.recommendation = finding.recommendation;
  entry.impact = finding.impact;
  entry.frequency = finding.frequency;
  entry.reach = finding.reach;
  entry.effort = finding.effort;
  entry.priority_score = finding.priority_score;
  entry.adr_candidate = finding.adr_candidate;

  finding.id = entry.id;
  finding.adr = entry.adr;
}

for (const [key, entry] of byKey) {
  if (seenKeys.has(key)) continue;
  if (entry.status === 'open') entry.status = 'not_seen_last_run';
  else if (entry.status === 'not_seen_last_run') entry.status = 'resolved';
}

writeJson(registryPath, registry);
writeJson(outRunPath, run);
console.log(`registry atualizado (${registry.findings.length} findings totais); run-report anotado com IDs permanentes.`);
