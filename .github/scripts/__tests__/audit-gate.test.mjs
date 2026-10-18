// Cobre o portão do npm audit: high/critical fora da lista falha, aviso da
// lista passa, exceção que sumiu do audit falha, e o que vem só por
// dependência (via em string) não é contado duas vezes.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { avaliar } from '../audit-gate.mjs';

const EXCECOES = { 'GHSA-aaaa-aaaa-aaaa': 'motivo' };

function aviso(id, severity, title = 't') {
  return { severity, title, url: `https://github.com/advisories/${id}` };
}

test('aviso high fora da lista bloqueia', () => {
  const audit = { vulnerabilities: { vue: { via: [aviso('GHSA-bbbb-bbbb-bbbb', 'high', 'XSS')] }, braces: { via: [aviso('GHSA-aaaa-aaaa-aaaa', 'high')] } } };
  const { bloqueados, naoUsadas } = avaliar(audit, EXCECOES);
  assert.equal(bloqueados.length, 1);
  assert.match(bloqueados[0], /vue: XSS/);
  assert.deepEqual(naoUsadas, []);
});

test('aviso critical fora da lista bloqueia', () => {
  const audit = { vulnerabilities: { x: { via: [aviso('GHSA-cccc-cccc-cccc', 'critical')] }, braces: { via: [aviso('GHSA-aaaa-aaaa-aaaa', 'high')] } } };
  assert.equal(avaliar(audit, EXCECOES).bloqueados.length, 1);
});

test('moderate e low não bloqueiam', () => {
  const audit = { vulnerabilities: { esbuild: { via: [aviso('GHSA-dddd-dddd-dddd', 'low')] }, y: { via: [aviso('GHSA-eeee-eeee-eeee', 'moderate')] }, braces: { via: [aviso('GHSA-aaaa-aaaa-aaaa', 'high')] } } };
  assert.deepEqual(avaliar(audit, EXCECOES), { bloqueados: [], naoUsadas: [] });
});

test('pacote que só herda o aviso (via em string) não bloqueia', () => {
  const audit = { vulnerabilities: { braces: { via: [aviso('GHSA-aaaa-aaaa-aaaa', 'high')] }, micromatch: { via: ['braces'] }, nuxt: { via: ['micromatch'] } } };
  assert.deepEqual(avaliar(audit, EXCECOES), { bloqueados: [], naoUsadas: [] });
});

test('exceção que não aparece mais no audit falha', () => {
  const { bloqueados, naoUsadas } = avaliar({ vulnerabilities: {} }, EXCECOES);
  assert.deepEqual(bloqueados, []);
  assert.deepEqual(naoUsadas, ['GHSA-aaaa-aaaa-aaaa']);
});
