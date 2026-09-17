#!/usr/bin/env node
// Última etapa do pipeline: escolhe o baseline correto (mesmo trigger +
// mesma branch; se não achar, cai pro run anterior mais recente marcado
// como aproximado — nunca finge uma comparação que não é real), calcula
// tendência, e escreve todas as views geradas: reports/latest/*,
// reports/history/*, reports/registry/{history,metrics}.json e
// reports/debt-register.md. Roda depois de merge-findings.mjs, então todo
// finding em run.findings já tem ID permanente.
import { appendFileSync } from 'node:fs';
import path from 'node:path';
import { readJson, writeJson, writeText, parseArgs, fail } from './lib.mjs';

const args = parseArgs(process.argv.slice(2));
const runPath = args._[0];
const reportsRoot = args['reports-root'] ?? 'reports';
if (!runPath) fail('uso: render-report.mjs <run-report.json> [--reports-root=reports]');

const run = readJson(runPath);
const registryDir = path.join(reportsRoot, 'registry');
const findingsPath = path.join(registryDir, 'findings.json');
const historyPath = path.join(registryDir, 'history.json');
const metricsPath = path.join(registryDir, 'metrics.json');

const findingsRegistry = readJson(findingsPath);
const history = readJson(historyPath);
const metrics = readJson(metricsPath);

// --- baseline ---
const sameTriggerBranch = history.runs.filter((r) => r.trigger === run.meta.trigger && r.branch === run.meta.branch);
let baseline = null;
let baselineNote = null;
if (sameTriggerBranch.length > 0) {
  baseline = sameTriggerBranch[sameTriggerBranch.length - 1];
} else if (history.runs.length > 0) {
  baseline = history.runs[history.runs.length - 1];
  baselineNote = 'aproximado (sem run comparável exato)';
}

const trend = {
  overall_score: baseline ? Math.round((run.overall_score - baseline.overall_score) * 100) / 100 : null,
  sections: run.sections.map((s) => {
    const prior = baseline?.section_scores?.[s.agent];
    return { agent: s.agent, delta: prior !== undefined ? Math.round((s.score - prior) * 100) / 100 : null };
  }),
  baseline: baseline
    ? { commit: baseline.commit, branch: baseline.branch, date: baseline.date, note: baselineNote }
    : { note: 'nenhum run anterior — primeira execução' },
};

// --- reports/latest/latest.json ---
const latest = {
  schema_version: '1.0.0',
  meta: run.meta,
  overall_score: run.overall_score,
  sections: run.sections,
  findings: run.findings,
  possible_regressions: run.possible_regressions ?? [],
  trend,
};
writeJson(path.join(reportsRoot, 'latest', 'latest.json'), latest);

// --- reports/latest/latest.md ---
const severityIcon = { critical: '🔴', high: '🟠', medium: '🟡', low: '🟢' };
const md = [];
md.push('# Relatório de auditoria — Klipper');
md.push('');
md.push('> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.');
md.push('');
md.push(`**Trigger:** ${run.meta.trigger} · **Branch:** ${run.meta.branch} · **Commit:** \`${run.meta.commit}\` · **Modo:** ${run.meta.depth}`);
md.push('');
// O score por seção e o `overall_score` não são renderizados. Cada agente
// atribui o score da sua seção por julgamento próprio, a cada execução (ver
// `_shared-contract.md`), e o `overall_score` é só a média deles em
// `aggregate-report.mjs` — nenhum dos dois é derivado dos findings. O resultado
// é uma nota que se move sozinha: entre `5342ab0` (29) e `71280c9` (70.33) não
// mudou uma linha de código de aplicação, só `dependabot.yml`, os próprios
// relatórios, a versão do `actions/checkout` e um teto de turnos; Segurança foi
// de 8 para 78 e Domínio financeiro de 7 para 55. Série completa:
// 62.67 → 73 → 48.67 → 29 → 70.33.
//
// Não é falta de cobertura disfarçada: o contrato manda baixar a nota quando o
// agente não conseguiu avaliar a seção, mas os dois runs acima gastaram esforço
// equivalente (45/67/56 e 64/69/51 turnos). Essa regra ainda confunde "saúde do
// código" com "quanto o agente olhou", e é uma segunda razão para não publicar
// o número como métrica.
//
// Os valores crus seguem em `latest.json` e `registry/{history,metrics}.json`
// para quem quiser investigar; o que sai daqui é só a apresentação deles.
md.push('## Seções');
md.push('');
md.push('| Seção | Risco |');
md.push('|---|---|');
for (const s of run.sections) {
  md.push(`| ${s.name} | ${s.risk} |`);
}
md.push('');
if (latest.possible_regressions.length > 0) {
  md.push('## Possible Regressions');
  md.push('');
  for (const r of latest.possible_regressions) {
    md.push(`- **${r.id ?? r.natural_key}** — ${r.previous_severity} → ${r.current_severity}: ${r.evidence}`);
  }
  md.push('');
}
md.push('## Findings priorizados (RICE)');
md.push('');
md.push('| ID | Severidade | Categoria | Prioridade | Descrição |');
md.push('|---|---|---|---|---|');
for (const f of [...run.findings].sort((a, b) => b.priority_score - a.priority_score).slice(0, 30)) {
  md.push(`| ${f.id ?? '—'} | ${severityIcon[f.severity] ?? ''} ${f.severity} | ${f.category} | ${f.priority_score} | ${f.description} |`);
}
md.push('');
const mdText = md.join('\n');
writeText(path.join(reportsRoot, 'latest', 'latest.md'), mdText);

// --- reports/history/<data>-<commit>.json (arquivo imutável desta execução) ---
const shortCommit = (run.meta.commit || 'unknown').slice(0, 7);
const dateSlug = run.meta.date.slice(0, 10);
writeJson(path.join(reportsRoot, 'history', `${dateSlug}-${shortCommit}.json`), latest);

// --- reports/registry/history.json ---
history.runs.push({
  date: run.meta.date,
  trigger: run.meta.trigger,
  commit: run.meta.commit,
  branch: run.meta.branch,
  depth: run.meta.depth,
  baseline: baseline ? { branch: baseline.branch, commit: baseline.commit } : null,
  overall_score: run.overall_score,
  section_scores: Object.fromEntries(run.sections.map((s) => [s.agent, s.score])),
});
writeJson(historyPath, history);

// --- reports/registry/metrics.json ---
for (const s of run.sections) {
  if (!metrics.series[s.agent]) metrics.series[s.agent] = [];
  metrics.series[s.agent].push({ date: run.meta.date, commit: run.meta.commit, score: s.score });
}
writeJson(metricsPath, metrics);

// --- reports/debt-register.md (view gerada de findings.json) ---
const openFindings = findingsRegistry.findings
  .filter((f) => f.status !== 'resolved')
  .sort((a, b) => (b.priority_score ?? 0) - (a.priority_score ?? 0));
const debt = [];
debt.push('# Registro de dívida técnica — Klipper');
debt.push('');
debt.push('> Gerado automaticamente por `render-report.mjs` a partir de `reports/registry/findings.json`.');
debt.push('> Não editar manualmente — mudanças aqui serão sobrescritas na próxima execução.');
debt.push('');
debt.push('| ID | Categoria | Descrição | Criado em | Última ocorrência | Impacto | Esforço | Prioridade |');
debt.push('|---|---|---|---|---|---|---|---|');
for (const f of openFindings) {
  debt.push(
    `| ${f.id} | ${f.category} | ${f.description ?? f.natural_key} | ${f.first_seen.date.slice(0, 10)} | ${f.last_seen.date.slice(0, 10)} | ${f.impact ?? '—'} | ${f.effort ?? '—'} | ${f.priority_score ?? '—'} |`
  );
}
debt.push('');
writeText(path.join(reportsRoot, 'debt-register.md'), debt.join('\n'));

// --- $GITHUB_STEP_SUMMARY ---
if (process.env.GITHUB_STEP_SUMMARY) {
  appendFileSync(process.env.GITHUB_STEP_SUMMARY, `${mdText}\n`);
}

console.log(
  `Relatório renderizado: overall_score=${run.overall_score}, ${openFindings.length} findings abertos, ` +
    `baseline=${baseline ? baseline.commit : 'nenhum'}.`
);
