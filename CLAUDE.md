# CLAUDE.md — Klipper · Contexto de Sessão
> Leia este arquivo PRIMEIRO. Carregue os complementares conforme a tarefa.

---

## IDENTIDADE

**Klipper** — Wealth Operating System pessoal de Roberto Milet.
Stack: Python · Streamlit Cloud · Supabase (PostgreSQL) · LiteLLM · NVIDIA NIM
Prod: https://klipper.streamlit.app | Repo: https://github.com/Borussia80/Klipper
Local: `/home/rmilet/Base/01-Projetos/11-Klipper/Klipper`

---

## ARQUIVOS COMPLEMENTARES — carregue só o necessário

| Se a tarefa envolve… | Carregue |
|---|---|
| `core/` ou `models/` | `CLAUDE-arch.md` |
| `pages/` ou UI/UX | `CLAUDE-ux.md` |
| Novo arquivo ou novo teste | `CLAUDE-process.md` |
| Bug com histórico de mudança | `CLAUDE-log.md` |

---

## ESCOPO PADRÃO — restrições de leitura

- **NÃO** leia `tests/` a menos que solicitado explicitamente.
- **NÃO** leia `migrations/` a menos que a tarefa seja de schema.
- **NÃO** toque em `bot/` — Fase 6, pendente, fora de escopo.
- Para entender um padrão existente: leia **um** arquivo de referência, não o diretório inteiro.
- Referência de qualidade para charts Plotly: `pages/7_Orcamento.py` (tem gauge + line funcionando).
- Referência de qualidade para testes: `tests/test_dashboard_charts.py` (18 testes TDD recentes).

---

## EXECUÇÃO LOCAL

```bash
cd /home/rmilet/Base/01-Projetos/11-Klipper/Klipper
export PATH="$HOME/.local/bin:$PATH"
streamlit run app.py
python -m pytest tests/ -q --tb=short   # suite rápida
python -m pytest tests/ -v               # saída completa
```

---

## REGRA DE OURO DO AGENTE

Matemática ancora. Narrativa sem evidência não altera decisão.
Código sem teste não entra. Não existe "adicionar teste depois".
