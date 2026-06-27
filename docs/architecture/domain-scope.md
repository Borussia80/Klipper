# Escopo de Domínio — Klipper

**Atualizado:** 2026-06-14

## O Klipper é exclusivamente FINANCEIRO

O Klipper é um **Wealth Operating System** pessoal. Seu domínio é **dinheiro**: transações,
contas, cartões, faturas, parcelamento, orçamento, investimentos, decisões e patrimônio.

**Não é** sistema de registro de saúde, clínica, terapias ou reembolso médico.

## Domínios que NÃO pertencem ao Klipper

| Domínio | Sistema-de-registro | Observação |
|---|---|---|
| Saúde / reembolso do Pedro (consultas, NF, protocolo, cálculo Bradesco, PDFs) | **Gestor-Reembolsos** (app desktop PyQt6 + SQLite) | Removido do Klipper em 2026-06-14 |

### Histórico da remoção de Saúde

- **Código:** módulo de Saúde removido do PWA, do Streamlit (que também foi removido do
  projeto) e do backend (`core/health_repository.py`, `models/health.py`). Spec `fatia-6`
  marcada OBSOLETA.
- **Banco:** tabelas `health_professionals`, `reimbursement_requests`, `health_sessions`
  removidas pela **`migrations/009_drop_health_domain.sql`**.
- **Dados:** preservados no Gestor-Reembolsos (sistema-de-registro do domínio).

### Integração futura (financeira, não clínica)

Reembolso interessa ao Klipper **apenas como dinheiro** (a receber + recebido), via um
"resumo financeiro" que o Gestor publica e o Klipper lê — planejado como Fatia 7. Não é
reintroduzir gestão de saúde; é tratar o reembolso como uma linha financeira.

## Regra

Antes de adicionar qualquer entidade/tabela nova, perguntar: **isto é dinheiro?** Se a
resposta for "é saúde / clínica / documento médico", o lugar é o Gestor-Reembolsos, não o Klipper.
