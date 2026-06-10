# CLAUDE-process.md — Klipper · Processo de Desenvolvimento
> Carregue este arquivo ao criar qualquer novo arquivo ou novo teste.

---

## TDD — CICLO OBRIGATÓRIO

```
① Red    — escreva o teste que descreve o comportamento. Ele DEVE falhar.
② Green  — escreva o mínimo de código para o teste passar. Exatamente o mínimo.
③ Refactor — melhore o design. Nenhum teste pode quebrar.
```

**Regras sem exceção:**
- Código sem teste correspondente não é aceito em nenhuma função pública.
- O teste é escrito **antes** do código. Sempre.
- Um teste escrito após o código é auditoria post-mortem — não é TDD e não conta.
- Se há um bug: primeiro escreva o teste que o reproduz. Só então corrija.
- Features sem teste de aceitação não são iniciadas.

---

## F.I.R.S.T. — TODO TESTE SATISFAZ AS CINCO PROPRIEDADES

| Letra | Atributo | Regra concreta neste repo |
|---|---|---|
| **F** | Fast | Suite completa < 10 s. I/O de rede (yfinance, BCB, Supabase) sempre mockado. Testes lentos marcados `@pytest.mark.slow`. |
| **I** | Independent | Nenhum teste depende de estado de outro. Fixtures `autouse` isolam `st.session_state`, cache Redis (`fakeredis` dedicado), circuit breakers (`cb.reset()` no setup) e repositórios (dados sintéticos). |
| **R** | Repeatable | Mesmo resultado em qualquer máquina, sem internet. `date.today()` substituído por datas absolutas futuras (ex: `date(2030, 1, 1)`). APIs externas sempre mockadas com `unittest.mock.patch` ou `MagicMock`. |
| **S** | Self-Validating | Passa ou falha — sem inspeção de stdout ou log. `assert` com mensagem clara obrigatório. `print()` dentro de teste é proibido. |
| **T** | Timely | Teste escrito **antes** do código de produção. Esta é a propriedade mais violada e a mais importante. |

---

## SRP — SINGLE RESPONSIBILITY PRINCIPLE

Cada módulo, classe e função tem **exatamente um motivo para mudar**.

**Heurísticas de detecção de violação:**
- Nome contém "e" ou "ou" → `processa_e_salva`, `valida_ou_formata` → responsabilidade dupla.
- Função ultrapassa ~25 linhas → questione a divisão. Acima de 40 linhas → divida.
- Adicionar feature exige modificar classe que "não deveria precisar mudar" → responsabilidade errada.

---

## PRÁTICAS XP

### Pair Programming
Toda sessão com Claude Code é pair programming assistido. Roberto define **o quê** e **por quê**. O agente executa, questiona e propõe. Roberto revisa cada diff antes de aceitar. O agente não faz commit sem aprovação explícita.

### Integração Contínua
GitHub Actions em todo push:
```
Ruff (lint) → mypy (tipos) → pytest (testes) → cobertura ≥ 80%
```
Nenhum merge com CI vermelho. "Vou corrigir depois do merge" não existe.

### Refactoring Contínuo
Não é sprint separado. Acontece no passo **Refactor** de cada ciclo TDD.

**Sinais que disparam refactoring imediato:**
- Duplicação de lógica (DRY)
- Função > ~25 linhas
- Classe com mais de uma responsabilidade (SRP)
- Teste que depende de outro teste (F.I.R.S.T.-I)
- Nome que precisa de comentário para ser entendido

### Feedback Curto

| Camada | Meta |
|---|---|
| Suite local (pytest) | < 10 s |
| CI completo (Actions) | < 3 min |
| Review de PR | mesmo dia útil |
| Deploy em produção | automático após merge em `main` |

---

## TEMPLATE DE NOVO MÓDULO

```python
# core/meu_modulo.py
"""Uma frase descrevendo a única responsabilidade deste módulo."""

# imports

class MinhaClasse:
    """Responsabilidade: [uma frase]."""

    def metodo_publico(self, ...) -> ...:
        """Comportamento esperado em uma frase."""
        ...
```

```python
# tests/test_meu_modulo.py
"""Testes TDD para core/meu_modulo.py."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date

class TestMinhaClasse:
    def test_comportamento_esperado(self):
        # Arrange
        ...
        # Act
        resultado = ...
        # Assert
        assert resultado == esperado, "mensagem clara do que falhou"
```
