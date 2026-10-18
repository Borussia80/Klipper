# Spec 03 — Transações (Movimento)

**Rota:** `/transacoes` · **Prioridade:** 2 · **Referências:** densidade S4, gestos C4, filtro em árvore E1.

## Hoje

Lista agrupada por dia, filtro Todos/Entradas/Saídas, densidade compacta/confortável, seleção e exclusão em massa.
Falta: filtro por conta/categoria/portador, busca, edição em massa de categoria, gestos, totais por dia.

## Desktop (≥ 768 px)

Cabeçalho fixo: título + mês (seletor ‹ outubro de 2026 ›) + contagem. Abaixo, barra de filtros:
`Busca` · `Tipo` (segmento) · `Conta ▾` · `Categoria ▾` (árvore, marcar pai marca filhas) · `Portador ▾` ·
[Limpar filtros]. Filtros ativos viram chips removíveis.

Tabela (densidade compacta = 36 px/linha; confortável = 48 px):

| ☐ | Descrição (+ subtítulo: categoria · conta) | Portador | Valor (direita, tabular) |

Cabeçalho de dia: "SEX, 16 DE OUT" à esquerda, **saldo do dia** (soma com sinal) à direita em `--t3`.
Clique na linha abre o modal de edição (existente). Seleção mostra barra de lote: **Mudar categoria**, Mudar conta
(`assign_account` existente), Excluir.

## Mobile (< 768 px)

Linha: ícone da categoria (neutro) · descrição / categoria · valor. Busca e filtros num botão "Filtrar" que abre
folha inferior.
- **Arrastar para a esquerda** revela [Excluir]; soltar além de 60 % exclui direto, com toast "Lançamento
  excluído." [Desfazer] (5 s).
- **Arrastar para a direita** revela [Categoria] → abre seletor.
- **Toque longo** entra em modo seleção (barra de lote no rodapé, acima da navegação).

## Valores e cor

Saída: "− R$ 23,50" em `--t1`. Entrada: "+ R$ 5.000,00" em `--t1` peso 600. **Sem verde/vermelho.**
Cor só para: parcela de compra sem fatura correspondente (aviso), lançamento duplicado suspeito (aviso, ícone).

## Dados

`GET /transactions` com cursor (`X-Next-Cursor`) — rolagem infinita já existente. Filtros que **já existem** no
controller: `year`/`month`, `account_id`, `member_id`, `type`. **Novos:** `category_id[]` (inclui filhas) e `q`
(busca na descrição).
**Novo** `POST /transactions/bulk_update` (`ids[]`, `category_id`) — ou estender o padrão do `assign_account`.

## Estados

| Estado | Texto |
|---|---|
| Vazio no mês | "Nenhum lançamento em outubro." [Adicionar] [Importar extrato] |
| Vazio por filtro | "Nada com esses filtros." [Limpar filtros] |
| Carregando mais | 3 linhas de esqueleto no fim |
| Erro | "Não foi possível carregar os lançamentos." [Tentar de novo] |

## Critérios de aceite

1. Filtrar por categoria pai traz também as filhas.
2. Mudar categoria de 20 lançamentos selecionados: 1 requisição, 1 toast, lista atualizada.
3. Exclusão por gesto é desfeita pelo toast e o lançamento volta na mesma posição.
4. Nenhum valor colorido em estado normal.
5. Testes: filtro em árvore (unidade), gesto (componente com eventos de ponteiro), bulk update (request spec Rails).
