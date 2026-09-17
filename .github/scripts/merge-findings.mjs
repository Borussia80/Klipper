#!/usr/bin/env node
// Casa os findings do run-report.json contra reports/registry/findings.json
// por natural_key, atribui/preserva o ID permanente
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

// Calculado antes da deduplicação abaixo, de propósito: o maior sequencial
// precisa contar também os IDs que a deduplicação absorve, para que um finding
// novo nunca reutilize um número já comunicado (ex: FIN-006).
const nextSeq = {};
for (const f of registry.findings) {
  const [prefix, seqStr] = f.id.split('-');
  nextSeq[prefix] = Math.max(nextSeq[prefix] ?? 0, Number(seqStr));
}

// Chaveado por natural_key só. Com a categoria na chave, o mesmo defeito visto
// por dois agentes recebia dois IDs permanentes, e consertar o código resolvia
// apenas o ID cuja categoria ainda casasse — o outro ficava aberto para sempre.
// O aggregate-report já colapsou repetições dentro do run; aqui a garantia é a
// de que o ID permanente é reencontrado mesmo que o defeito passe a ser
// reportado por outro agente.
const byKey = new Map();
for (const f of registry.findings) {
  const existing = byKey.get(f.natural_key);
  // Registro migrado tem no máximo uma entrada por chave. Se ainda houver par
  // remanescente, sobrevive o de first_seen mais antigo — é o ID que já foi
  // comunicado — e o outro é anotado em merged_from em vez de virar órfão.
  if (!existing) {
    byKey.set(f.natural_key, f);
  } else if (f.first_seen.date < existing.first_seen.date) {
    f.merged_from = [...(f.merged_from ?? []), existing.id];
    f.occurrences = Math.max(f.occurrences, existing.occurrences);
    byKey.set(f.natural_key, f);
  } else {
    existing.merged_from = [...(existing.merged_from ?? []), f.id];
    existing.occurrences = Math.max(existing.occurrences, f.occurrences);
  }
}
registry.findings = [...byKey.values()];
const seenKeys = new Set();

for (const finding of run.findings) {
  const key = finding.natural_key;
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
