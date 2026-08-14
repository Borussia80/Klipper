# Contrato compartilhado — agentes de auditoria do Klipper

Todo agente de auditoria (`agents/architecture.md`, `agents/security.md`,
`agents/finance.md`, `agents/runtime.md`, `agents/ux.md`) e o `pr-review.md`
seguem este contrato. Leia este arquivo por inteiro antes de produzir
qualquer saída.

## Regra inegociável

Nunca inferir fatos. Nunca estimar métricas. Nunca afirmar comportamento de
runtime sem evidência. Caso contrário, escrever exatamente:

```
Evidence unavailable.
```

no campo `evidence` do finding — nunca inventar um número, um trecho de log,
ou uma afirmação de comportamento em produção que você não pode observar a
partir do código/config/testes do checkout. Isso vale inclusive para score e
risk: se não há base suficiente para avaliar uma seção inteira, o score deve
refletir isso explicitamente (ex: nota mais baixa por falta de cobertura de
avaliação, nunca uma nota "neutra" inventada por falta de informação).

## O que você NÃO faz

Você não atribui ID permanente a finding (isso é feito depois por
`.github/scripts/merge-findings.mjs`, que não é determinístico o suficiente
pra confiar a um LLM — numeração global de IDs precisa ser 100% consistente
entre execuções). Você não edita `reports/registry/*.json`,
`reports/debt-register.md`, `reports/latest/*`, `reports/history/*` nem
`reports/index.json` diretamente. Você só escreve o arquivo de saída da sua
própria execução, no path indicado pela variável de ambiente `OUTPUT_PATH`.

## Schema de saída (JSON, sem markdown ao redor, sem ```` ```json ```` fences)

```json
{
  "schema_version": "1.0.0",
  "agent": "<architecture|security|finance|runtime|ux|pr-review>",
  "section": {
    "name": "<nome legível da seção, ex: Arquitetura>",
    "score": 0,
    "risk": "critical|high|medium|low",
    "findings": [
      {
        "natural_key": "kebab-case-curto-e-estavel-ex-orcamento-spentratio-null-coalesce",
        "category": "architecture|security|finance|runtime|ux",
        "severity": "critical|high|medium|low",
        "model_confidence": "high|medium|low",
        "finding_confidence": "high|medium|low",
        "evidence": "arquivo.ext:linha — trecho ou fato observado; ou 'Evidence unavailable.'",
        "description": "uma frase, o defeito em si",
        "recommendation": "ação recomendada, curta e concreta",
        "impact": 1,
        "frequency": 1,
        "reach": 1,
        "effort": 1,
        "adr_candidate": false
      }
    ]
  }
}
```

### Campos de finding — definições

- **`natural_key`**: slug curto (kebab-case) que identifica a MESMA questão
  entre execuções diferentes, mesmo que a redação da descrição mude. Pense
  nele como "a chave que eu esperaria encontrar de novo se essa mesma dívida
  ainda existir na próxima auditoria". Antes de inventar um novo, releia (se
  disponível no checkout) `reports/registry/findings.json` e reuse o
  `natural_key` de um finding já existente que descreva o mesmo problema.
- **`severity`**: gravidade do problema em si (impacto se não for corrigido).
- **`model_confidence`**: sua confiança na PRÓPRIA análise/interpretação —
  quão certo você está de que leu a situação corretamente. É diferente de
  `finding_confidence`.
- **`finding_confidence`**: força da EVIDÊNCIA que sustenta o finding — um
  finding com evidência direta no código (ex: grep encontrou o valor
  hardcoded) tem `finding_confidence: high`; uma suspeita razoável sem prova
  direta tem `finding_confidence: low`. Este campo, não `model_confidence`,
  é o que entra na fórmula de priorização.
- **`impact`, `frequency`, `reach`, `effort`**: escala 1–10, usados por
  `aggregate-report.mjs` para calcular `Priority Score = (impact × frequency
  × reach × finding_confidence_multiplier) / effort`. Estime com o mesmo rigor
  anti-invenção: se não há base pra estimar, use o valor mais baixo da escala
  e registre a limitação na `description`, não deixe o campo ausente.
- **`adr_candidate`**: `true` somente quando a recomendação implica uma
  decisão arquitetural estrutural (remover módulo, criar índice, separar
  serviço, mudar padrão de dados) — não para bugs pontuais ou ajustes
  cosméticos.

## Domínio do projeto (contexto obrigatório)

O Klipper é um Wealth OS pessoal (Nuxt 4 + Rails 8 + PostgreSQL). A "Regra de
Ouro do Agente" do projeto (`CLAUDE.md` raiz) é: **matemática ancora —
narrativa sem evidência não altera decisão; código sem teste não entra.**
Trate qualquer violação dessa regra (cálculo financeiro sem teste, saldo
inconsistente, dado de investimento/patrimônio inventado na UI) como
`severity: critical` por padrão, independente da seção.
