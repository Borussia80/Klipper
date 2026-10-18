#!/usr/bin/env node
// Portão do `npm audit` com lista de exceções explícita, aprovada pelo
// mantenedor em 2026-10-17. O `npm audit --audit-level=high` não aceita
// ignorar um aviso, então um aviso sem versão corrigida publicada deixava o CI
// vermelho em todo PR — e um portão que fica vermelho sem saída é um portão
// que se aprende a ignorar (SEC-003). Aqui só passa o que está em EXCECOES,
// com o motivo escrito; o resto de high/critical falha como antes. Exceção
// que deixou de aparecer também falha, para a lista não apodrecer.
//
// uso: npm audit --json > audit.json; node audit-gate.mjs audit.json
import { readJson, parseArgs, fail } from './lib.mjs';

const BLOQUEIA = new Set(['high', 'critical']);

// Revisar a cada atualização do nuxt: quando sair versão corrigida, o aviso
// some do audit e a exceção passa a falhar como não usada.
export const EXCECOES = {
  // braces <=3.0.3 (última publicada é 3.0.3). DoS por padrão glob aninhado;
  // entra via nitropack → globby → micromatch, só no build, com padrões do
  // próprio repo — nenhuma entrada de usuário chega até ele.
  'GHSA-vfj7-8cjw-p6xm': 'braces sem versão corrigida; só no build',
  // node-forge <=1.4.0 (última publicada é 1.4.0). Falha na verificação de
  // assinatura RSA; entra via @nuxt/cli → listhen, que só gera o certificado
  // do servidor de desenvolvimento. O SPA publicado não carrega o node-forge.
  'GHSA-86w9-cpqp-85rv': 'node-forge sem versão corrigida; só no dev server',
};

export function avaliar(audit, excecoes = EXCECOES) {
  const vistos = new Set();
  const bloqueados = [];
  for (const [pacote, vuln] of Object.entries(audit.vulnerabilities ?? {})) {
    // Entradas de `via` que são string apontam para outro pacote da lista; o
    // aviso de verdade está no objeto, no pacote de origem.
    for (const aviso of vuln.via) {
      if (typeof aviso !== 'object' || !BLOQUEIA.has(aviso.severity)) continue;
      const id = aviso.url?.split('/').pop();
      if (id in excecoes) {
        vistos.add(id);
      } else {
        bloqueados.push(`${aviso.severity} ${pacote}: ${aviso.title} (${aviso.url})`);
      }
    }
  }
  const naoUsadas = Object.keys(excecoes).filter((id) => !vistos.has(id));
  return { bloqueados, naoUsadas };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const args = parseArgs(process.argv.slice(2));
  if (!args._[0]) fail('uso: audit-gate.mjs <audit.json>');
  const { bloqueados, naoUsadas } = avaliar(readJson(args._[0]));
  for (const linha of bloqueados) console.error(linha);
  for (const id of naoUsadas) console.error(`exceção sem uso, remova de EXCECOES: ${id}`);
  if (bloqueados.length || naoUsadas.length) process.exit(1);
  console.log(`npm audit ok (${Object.keys(EXCECOES).length} exceções em uso)`);
}
