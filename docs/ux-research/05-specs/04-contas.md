# Spec 04 — Contas e detalhe de conta

**Rotas:** `/contas` (existente, rótulo "Carteiras") e **nova** `/contas/[id]`. · **Prioridade:** 2 ·
**Referências:** agrupamento S2, gráfico de saldo S3.

## Lista `/contas`

Grupos fixos, nesta ordem, cada um com subtotal à direita do título:

1. **Contas** (corrente, poupança, carteira) — subtotal = soma de `balance`
2. **Cartões** — subtotal = soma de `saldo_fatura_atual`, rotulado "a pagar"
3. **Investimentos** — subtotal = custo (de `investments/portfolio`); link para `/investimentos`

Linha: ícone do banco (pequeno, com a cor do banco — decisão de 2026-10-17) · nome / instituição · indicador de
atualização · valor. Contas inativas recolhidas em "Arquivadas ({n})".

**Indicador de atualização:** se `saldo_atualizado_em` tem mais de 7 dias → aviso neutro com ícone de relógio e
texto "atualizado há 12 dias". Sem data → "saldo nunca conferido".

Desktop: grupos em painéis empilhados, largura total, linhas de 48 px. Mobile: mesma estrutura, sem colunas extras.

## Detalhe `/contas/[id]`

```
‹ Contas   Nubank — Conta            [Editar]
R$ 3.218,40              atualizado em 15/10
──── gráfico de saldo · [3m 6m 1a] ────
Cartão (se for): Fatura atual · Mínimo · Juros a.m. · Fecha dia X · Vence dia Y
──── Lançamentos desta conta (lista da spec 03 filtrada) ────
```

- Gráfico: saldo **reconstruído** a partir do saldo atual menos os lançamentos, dia a dia. Linha `--t2`; trecho
  abaixo de zero preenchido `--ald`; zero marcado quando o intervalo cruza zero.
- Cartão: os campos já existem (`saldo_fatura_atual`, `pagamento_minimo`, `juros_rotativo_am`, `iof_projetado`) e
  hoje ficam no modal de edição; aqui viram leitura. Juros rotativo acima de 10 % a.m. com fatura em aberto →
  faixa alta "Rotativo deste cartão custa {x}% ao mês." (reaproveita a lógica do `debt_ranking`).
- Fechamento e vencimento: **campos novos** `accounts.dia_fechamento` e `accounts.dia_vencimento` (1–31, só
  cartão), migrados juntos. Dia maior que o mês → último dia do mês; vencimento em fim de semana ou feriado →
  próximo dia útil; fechamento não se desloca. Fonte dos feriados: definida na análise de domínio.

## Dados

| Bloco | Fonte |
|---|---|
| Lista | `GET /accounts`, `GET /investments/portfolio` |
| Detalhe | `GET /accounts/:id` |
| Série de saldo | **novo** `GET /accounts/:id/balance_history?period=6m` → `[{date, balance}]` (calculado no Rails: saldo atual menos soma acumulada dos lançamentos posteriores a cada dia) |
| Lançamentos | `GET /transactions?account_id=:id` (filtro da spec 03) |

## Estados

- Sem contas: "Cadastre a primeira conta para o Klipper calcular seu patrimônio." [Adicionar conta]
- Conta sem lançamentos: gráfico some; "Esta conta ainda não tem lançamentos. O saldo mostrado é o informado."
- Erro na série: só o gráfico mostra erro com [Tentar de novo].

## Critérios de aceite

1. Subtotais batem com a soma das linhas (teste de componente).
2. `balance_history`: para uma conta com saldo 1.000 e um débito de 200 ontem, o ponto de anteontem é 1.200
   (request spec).
3. Conta negativa: valor em `--alert` com ícone e o mesmo alarme aparece no painel.
4. Voltar do detalhe preserva a rolagem da lista.
