import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import path from 'node:path';

export function readJson(filePath) {
  return JSON.parse(readFileSync(filePath, 'utf8'));
}

export function writeJson(filePath, data) {
  mkdirSync(path.dirname(filePath), { recursive: true });
  writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, 'utf8');
}

export function readText(filePath) {
  return readFileSync(filePath, 'utf8');
}

export function writeText(filePath, text) {
  mkdirSync(path.dirname(filePath), { recursive: true });
  writeFileSync(filePath, text.endsWith('\n') ? text : `${text}\n`, 'utf8');
}

export function parseArgs(argv) {
  const args = { _: [] };
  for (const raw of argv) {
    if (raw.startsWith('--')) {
      const [key, ...rest] = raw.slice(2).split('=');
      args[key] = rest.length ? rest.join('=') : true;
    } else {
      args._.push(raw);
    }
  }
  return args;
}

export function fail(message) {
  console.error(`Erro: ${message}`);
  process.exit(1);
}
