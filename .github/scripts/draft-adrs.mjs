#!/usr/bin/env node
// Parte determinística da geração de ADR: aloca o número sequencial,
// monta o front-matter (sempre status: proposed) e grava o arquivo em
// docs/adrs/proposed/. O corpo em prosa (Contexto/Decisão/Consequências)
// é produzido separadamente pelo claude-code-action com o prompt
// adr-draft.md — este script só recebe esse texto pronto via --body-file
// e nunca decide o conteúdo, só o envelope e a numeração.
//
// Modo --list: imprime em stdout (JSON) os findings elegíveis
// (adr_candidate=true, sem ADR vinculado, status != resolved) para o
// workflow iterar e chamar o claude-code-action uma vez por finding.
import { readdirSync, existsSync, mkdirSync } from 'node:fs';
import path from 'node:path';
import { readJson, writeJson, writeText, readText, parseArgs, fail } from './lib.mjs';

const args = parseArgs(process.argv.slice(2));
const registryPath = args.registry ?? 'reports/registry/findings.json';
const adrsRoot = args['adrs-root'] ?? 'docs/adrs';

if (args.list) {
  const registry = readJson(registryPath);
  const eligible = registry.findings.filter((f) => f.adr_candidate === true && !f.adr && f.status !== 'resolved');
  console.log(JSON.stringify(eligible));
  process.exit(0);
}

const findingId = args['finding-id'];
const bodyFile = args['body-file'];
if (!findingId || !bodyFile) {
  fail('uso: draft-adrs.mjs --finding-id=ARCH-018 --body-file=<path> [--registry=reports/registry/findings.json] [--adrs-root=docs/adrs]\n       draft-adrs.mjs --list [--registry=...]');
}

const registry = readJson(registryPath);
const entry = registry.findings.find((f) => f.id === findingId);
if (!entry) fail(`finding ${findingId} não encontrado em ${registryPath}`);
if (entry.adr) fail(`finding ${findingId} já tem ADR vinculado: ${entry.adr}`);

const proposedDir = path.join(adrsRoot, 'proposed');
mkdirSync(proposedDir, { recursive: true });

const seqPattern = /ADR-\d{4}-\d{2}-\d{2}-(\d+)\.md$/;
const existingSeqs = [
  ...readdirSync(proposedDir),
  ...(existsSync(adrsRoot) ? readdirSync(adrsRoot).filter((f) => f.endsWith('.md')) : []),
]
  .map((f) => Number((f.match(seqPattern) || [])[1]))
  .filter((n) => Number.isFinite(n));

const seq = (existingSeqs.length ? Math.max(...existingSeqs) : 0) + 1;
const date = new Date().toISOString().slice(0, 10);
const filename = `ADR-${date}-${String(seq).padStart(3, '0')}.md`;
const filePath = path.join(proposedDir, filename);

const body = readText(bodyFile);
const frontMatter = ['---', 'status: proposed', `finding: ${findingId}`, `date: ${date}`, '---', ''].join('\n');

writeText(filePath, frontMatter + body);

entry.adr = path.posix.join('docs/adrs/proposed', filename);
writeJson(registryPath, registry);

console.log(`ADR gravado em ${filePath}, vinculado ao finding ${findingId}.`);
