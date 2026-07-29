# PR Review (enxuto)

Este prompt roda em **todo Pull Request**. É deliberadamente mais leve que os
agentes de `agents/` — um único prompt, sem matriz, sem persistência em
`reports/registry/`. Objetivo: feedback rápido no próprio PR, não auditoria
completa.

## Regra inegociável

Mesma regra de `_shared-contract.md`: nunca inferir fatos, nunca estimar
métricas, nunca afirmar comportamento de runtime sem evidência. Sem evidência
suficiente, escreva exatamente `Evidence unavailable.` em vez de inventar.

## Escopo desta execução

**Só o diff do PR** (`git diff` contra a base branch), não o repositório
inteiro — isso é revisão de mudança, não auditoria completa (essa acontece em
release/deploy, via os 5 agentes especializados). Ignore arquivos sob
`reports/**` e `docs/adrs/**` (são gerados pelo próprio pipeline de
auditoria, não fazem parte da mudança do autor).

Avalie o diff nas mesmas 5 lentes dos agentes completos, mas só o que o diff
realmente toca:
- **Arquitetura/Qualidade**: a mudança introduz acoplamento novo, quebra uma
  camada existente, ou vem sem teste para lógica nova/alterada?
- **Segurança**: segredo novo no diff, validação de entrada removida,
  dependência nova sem necessidade clara.
- **Domínio financeiro**: qualquer cálculo financeiro tocado no diff tem
  teste cobrindo o novo comportamento? Trate ausência como bloqueante
  (`severity: critical`) — é a "Regra de Ouro do Agente" do `CLAUDE.md` raiz.
- **Performance/Confiabilidade**: só aponte se o diff em si evidenciar risco
  (ex: query nova sem `includes` num loop); não especule sobre produção.
- **Product Health**: a mudança deixa alguma rota/feature órfã, ou quebra
  consistência de UX visível no próprio diff.

## Formato de saída

Este prompt **não** segue o schema JSON de `_shared-contract.md` — a saída
é um comentário Markdown direto no PR (via `claude-code-action`), curto e
acionável:

```markdown
## Revisão automática

**Resumo**: <1-2 frases sobre o que o diff faz>

### Achados
- [severidade] <arquivo:linha> — <descrição curta> — <recomendação>
  (ou "Nenhum achado bloqueante nesta revisão.")

### Cobertura de teste
<uma frase: a mudança tem teste correspondente ou não>
```

Não crie `natural_key`, não gere ID permanente, não toque em
`reports/registry/*` — isso é exclusivo do fluxo de release/deploy
(`aggregate-report.mjs` / `merge-findings.mjs`). Se quiser sinalizar que algo
merece entrar no debt register formal, diga isso em texto no comentário; a
entrada oficial só acontece quando o próximo relatório completo (release ou
deploy) rodar os 5 agentes especializados sobre o código já mergeado.
