// Cobre a declaração de run incompleto no relatório (PIPE-1). Um analista que
// falha não anula mais os outros, mas o relatório que sai precisa dizer que é
// parcial: sem isso, "nenhum finding de segurança" fica indistinguível de
// "segurança não foi avaliada", que é a leitura errada mais cara possível.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'render-report.mjs');

function runRender({ missingAgents = [], sections }) {
  const dir = mkdtempSync(path.join(tmpdir(), 'render-report-'));
  const reportsRoot = path.join(dir, 'reports');
  mkdirSync(path.join(reportsRoot, 'registry'), { recursive: true });
  writeFileSync(path.join(reportsRoot, 'registry', 'findings.json'), JSON.stringify({ schema_version: '1.0.0', findings: [] }));
  writeFileSync(path.join(reportsRoot, 'registry', 'history.json'), JSON.stringify({ schema_version: '1.0.0', runs: [] }));
  writeFileSync(path.join(reportsRoot, 'registry', 'metrics.json'), JSON.stringify({ schema_version: '1.0.0', series: {} }));

  const runPath = path.join(dir, 'run.json');
  writeFileSync(runPath, JSON.stringify({
    meta: {
      date: '2026-09-17T00:00:00.000Z',
      trigger: 'workflow_run',
      depth: 'fast',
      branch: 'main',
      commit: 'aaa1112',
      missing_agents: missingAgents,
    },
    overall_score: 50,
    sections,
    findings: [],
    possible_regressions: [],
  }));

  execFileSync('node', [SCRIPT, runPath, `--reports-root=${reportsRoot}`], { stdio: 'pipe' });
  return readFileSync(path.join(reportsRoot, 'latest', 'latest.md'), 'utf8');
}

const architecture = { agent: 'architecture', name: 'Arquitetura', score: 50, risk: 'medium' };
const finance = { agent: 'finance', name: 'Domínio financeiro', score: 50, risk: 'medium' };
const security = { agent: 'security', name: 'Segurança', score: 50, risk: 'medium' };

test('avisa que o relatório é incompleto e nomeia a análise ausente', () => {
  const md = runRender({ missingAgents: ['security'], sections: [architecture, finance] });

  assert.match(md, /Relatório incompleto/);
  assert.match(md, /security/, 'nomeia qual análise faltou');
  assert.match(md, /2 das 3 seções esperadas/, 'diz o tamanho do vão, não só que existe');
});

test('não avisa nada quando todas as análises entregaram', () => {
  const md = runRender({ missingAgents: [], sections: [architecture, finance, security] });

  assert.doesNotMatch(md, /Relatório incompleto/);
});

test('não avisa nada num run-report antigo, sem o campo missing_agents', () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'render-report-legacy-'));
  const reportsRoot = path.join(dir, 'reports');
  mkdirSync(path.join(reportsRoot, 'registry'), { recursive: true });
  writeFileSync(path.join(reportsRoot, 'registry', 'findings.json'), JSON.stringify({ schema_version: '1.0.0', findings: [] }));
  writeFileSync(path.join(reportsRoot, 'registry', 'history.json'), JSON.stringify({ schema_version: '1.0.0', runs: [] }));
  writeFileSync(path.join(reportsRoot, 'registry', 'metrics.json'), JSON.stringify({ schema_version: '1.0.0', series: {} }));
  const runPath = path.join(dir, 'run.json');
  writeFileSync(runPath, JSON.stringify({
    meta: { date: '2026-09-17T00:00:00.000Z', trigger: 'release', depth: 'fast', branch: 'main', commit: 'bbb2223' },
    overall_score: 50,
    sections: [architecture],
    findings: [],
    possible_regressions: [],
  }));

  execFileSync('node', [SCRIPT, runPath, `--reports-root=${reportsRoot}`], { stdio: 'pipe' });
  const md = readFileSync(path.join(reportsRoot, 'latest', 'latest.md'), 'utf8');

  assert.doesNotMatch(md, /Relatório incompleto/);
});
