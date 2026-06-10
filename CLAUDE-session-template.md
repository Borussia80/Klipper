# CLAUDE-session-template.md — Templates de Sessão
> Copie o template adequado e cole no início de cada sessão no Claude Code.
> Substitua os campos entre [ ].

---

## TEMPLATE GENÉRICO

```
Sessão Klipper. Leia CLAUDE.md.

Tarefa: [UMA coisa específica]
Arquivo alvo: [caminho/do/arquivo.py]
Referência de padrão: [caminho/do/arquivo_referencia.py]

Não toque em outros arquivos sem avisar.
```

---

## TEMPLATE — NOVO CHART (Sprint UI/UX)

```
Sessão Klipper. Leia CLAUDE.md + CLAUDE-ux.md.

Tarefa: Sprint [N] — [nome do sprint]
Arquivo alvo: pages/[X_Pagina.py]
Funções de dados: criar em core/analytics.py
Testes TDD: tests/test_[pagina]_charts.py

Referência de qualidade para charts: pages/7_Orcamento.py
Referência de qualidade para testes: tests/test_dashboard_charts.py
CAT_COLORS já existe em core/styles.py — use direto.
Padrão Plotly está documentado em CLAUDE-ux.md.

Ciclo obrigatório: Red → Green → Refactor.
Não renderize nada antes de ter o teste passando.
```

---

## TEMPLATE — NOVO MÓDULO CORE

```
Sessão Klipper. Leia CLAUDE.md + CLAUDE-arch.md + CLAUDE-process.md.

Tarefa: Criar core/[nome_modulo.py]
Responsabilidade única: [uma frase]
Testes TDD: tests/test_[nome_modulo].py

Referência de testes: tests/test_dashboard_charts.py
Ciclo obrigatório: Red → Green → Refactor.
Função pública sem teste não é aceita.
```

---

## TEMPLATE — CORREÇÃO DE BUG

```
Sessão Klipper. Leia CLAUDE.md + CLAUDE-log.md.

Bug: [descrição do comportamento errado]
Arquivo suspeito: [caminho]
Comportamento esperado: [o que deveria acontecer]

Passo 1: escreva o teste que reproduz o bug (Red).
Passo 2: corrija o código (Green).
Passo 3: refatore se necessário.
Não corrija sem o teste primeiro.
```

---

## TEMPLATE — MOBILE FIX (Sprint 5)

```
Sessão Klipper. Leia CLAUDE.md + CLAUDE-ux.md (seção Sprint 5).

Tarefa: Mobile fix — [página específica ou "todas as páginas"]
Problema: st.columns([1, 4]) quebra em 390px — nav 840px preenche viewport.
Fix aprovado: CSS @media (max-width: 640px) oculta coluna nav.
Referência do fix já aplicado: app.py (tem o @media implementado).

Não altere lógica de negócio — apenas layout CSS.
```

---

## DICAS DE USO

- **Uma tarefa por sessão.** Sessões com escopo amplo ("melhore o projeto todo") desperdiçam tokens em inferência de contexto.
- **`/clear` entre sprints.** Depois que um sprint está testado e commitado, limpe o contexto.
- **`/add` seletivo.** Adicione só os arquivos do escopo da tarefa + a referência de padrão.
- **Nunca `/add tests/`.** O agente não precisa ler todos os testes existentes — só o arquivo de referência indicado no template.
