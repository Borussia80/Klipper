import { readFileSync } from 'node:fs'
import { pathToFileURL } from 'node:url'

function documentation(path) {
  return typeof path === 'string' &&
    (/^[^/]+\.md$/i.test(path) || /^docs\/(?!\.\.\/).+\.md$/i.test(path))
}

export function docsOnly({ event, files, count }) {
  if (event !== 'pull_request' || !Array.isArray(files) ||
      !Number.isInteger(count) || count < 1 || count >= 3000 || files.length !== count) return false
  return files.every(file => file && documentation(file.filename) &&
    (file.status !== 'renamed' || documentation(file.previous_filename)))
}

export function classifyResponse(response, event, count) {
  try {
    const pages = JSON.parse(response)
    return Array.isArray(pages) && pages.every(Array.isArray) &&
      docsOnly({ event, count, files: pages.flat() })
  } catch {
    return false
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  let result = false
  try {
    result = classifyResponse(readFileSync(process.argv[2], 'utf8'), process.env.CI_EVENT_NAME, Number(process.env.CI_CHANGED_FILES))
  } catch {
    // Falha de API ou dados inválidos exige a execução completa.
  }
  process.stdout.write(String(result))
}
