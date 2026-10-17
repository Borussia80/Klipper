# Spec 05 — Orçamento

**Rota:** `/orcamento` · **Prioridade:** 2 · **Referências:** fluxo C3, soma por categoria pai E1.

## Objetivo

Trocar "quanto já gastei" por **"quanto ainda posso gastar, e estou no ritmo?"**.

## Topo

Três números em linha (mobile: lista): **Limite do mês** · **Gasto** · **Disponível**. Abaixo, "Pode gastar
R$ {disponível ÷ dias restantes} por dia até {último dia}." Se disponível ≤ 0: faixa crítica "O orçamento do mês
acabou: {valor} acima do limite."

## Linha por categoria (envelope)

```
Mercado                                   R$ 412 de R$ 900
[██████████░░░░░░░░░░│░░░░░░░░]           sobram R$ 488 · R$ 32/dia
                     ↑ marcador do ritmo (dia 16 de 31 = 52 %)
```

- Trilho `--t4`, preenchimento `--t2` (neutro).
- **Marcador de ritmo:** traço vertical na posição `dia_atual / dias_do_mês`.
- Estado por cor, só quando anormal:
  - gasto > ritmo **e** categoria `recorrencia = rotineiro` → **aviso** (ícone + borda forte); categorias pontuais
    não disparam ritmo (uma conta anual não "corre na frente").
  - `pct_used > 100` → **crítico**: preenchimento `--alert`, texto "passou R$ {x}".
- Categoria pai com filhas: linha do pai mostra a soma; expandir revela as filhas com seus limites (se tiverem).

Ordenação padrão: crítico → aviso → maior % usado. Opção "Ordem alfabética".

## Interações

- Tocar no envelope abre os lançamentos do mês daquela categoria (spec 03 filtrada).
- Editar limite: toque no valor do limite vira campo inline (desktop) ou folha com teclado próprio (mobile, mesmo
  teclado da spec 02).
- "Copiar limites do mês anterior" quando o mês não tem orçamento — **novo** `POST /budgets/copy_previous`.

## Dados

`GET /budgets/summary` já devolve `amount_limit`, `spent`, `remaining`, `pct_used`, `recorrencia`. Ritmo e
gasto por dia são calculados no cliente a partir da data. Soma por pai depende da spec 07.

## Estados

- Sem orçamento no mês: "Outubro ainda não tem limites." [Copiar de setembro] [Definir limites]
- Categoria sem limite mas com gasto: grupo "Sem limite definido" ao fim, só com o valor gasto.
- Bug conhecido do roadmap (`spentRatio ?? 0` confunde "sem orçamento" com "0 %") é resolvido por estas regras: sem
  limite não tem barra.

## Critérios de aceite

1. No dia 16 de 31, categoria rotineira com 70 % gasto mostra aviso; com 40 %, não.
2. Categoria pontual com 70 % no dia 5 não mostra aviso.
3. Acima de 100 % mostra crítico e o mesmo alarme aparece no painel.
4. Testes de unidade para ritmo e por-dia (inclui último dia do mês e mês de 28 dias).
