import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { docsOnly, classifyResponse } from '../ci-scope.mjs'

const pr = (files, count = files.length) => ({ event: 'pull_request', files, count })
const file = (filename, extra = {}) => ({ filename, status: 'modified', ...extra })

describe('seleção de escopo do CI', () => {
  it('dispensa suítes apenas em PR com documentação reconhecida', () => {
    assert.equal(docsOnly(pr([file('CLAUDE.md'), file('docs/alpha/guia.md')])), true)
  })
  it('executa tudo no push e em arquivos de código, configuração ou documentação de app', () => {
    for (const name of ['.github/workflows/ci.yml', 'apps/klipper-web/README.md', 'docs/script.sh', 'package.json']) {
      assert.equal(docsOnly(pr([file(name)])), false, name)
    }
    assert.equal(docsOnly({ event: 'push', files: [file('README.md')], count: 1 }), false)
    assert.equal(docsOnly(pr([file('README.md'), file('apps/klipper-api/Gemfile')])), false)
  })
  it('considera também o caminho anterior em renomeações', () => {
    assert.equal(docsOnly(pr([file('docs/guia.md', { status: 'renamed', previous_filename: 'apps/api.rb' })])), false)
    assert.equal(docsOnly(pr([file('docs/novo.md', { status: 'renamed', previous_filename: 'docs/velho.md' })])), true)
    assert.equal(docsOnly(pr([file('docs/novo.md', { status: 'renamed' })])), false)
  })
  it('executa tudo quando a lista é vazia, incompleta, inválida ou excede o limite da API', () => {
    assert.equal(docsOnly(pr([])), false)
    assert.equal(docsOnly(pr([file('README.md')], 2)), false)
    assert.equal(docsOnly(pr([file('README.md')], 3000)), false)
    assert.equal(docsOnly({ event: 'pull_request', files: null, count: 1 }), false)
    assert.equal(docsOnly(pr([{ status: 'modified' }])), false)
  })
  it('executa tudo quando a resposta da API é inválida ou incompleta', () => {
    assert.equal(classifyResponse('inválido', 'pull_request', 1), false)
    assert.equal(classifyResponse(JSON.stringify([[file('README.md')]]), 'pull_request', 2), false)
    assert.equal(classifyResponse(JSON.stringify([[file('README.md')]]), 'pull_request', 1), true)
  })
})
