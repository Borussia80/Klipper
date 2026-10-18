# Spec 07 — Categorias em dois níveis

**Onde:** seção em `/configuracoes` (hoje categorias só são criadas por modal) + seletores em lançamento, filtro e
orçamento. · **Prioridade:** 2 (é dependência das specs 02, 03 e 05) · **Referência:** E1.

## Regra

Dois níveis **fixos**: categoria-pai e subcategoria. Subcategoria não tem filhas. Transação pode apontar para pai ou
filha. `natureza` e `category_type` da filha herdam do pai (não editáveis na filha) — mantém o split
Fixo × Cartão × Variável coerente.

## Tela de gestão

Lista por tipo (Saídas / Entradas). Cada pai com suas filhas indentadas; arrastar para reordenar (desktop: alça;
mobile: modo "Reordenar"). Ações por linha: renomear, mudar ícone, adicionar subcategoria, ocultar, mesclar em outra.

- **Ocultar** em vez de excluir quando há lançamentos: some dos seletores, continua nos relatórios.
- **Mesclar:** move os lançamentos e orçamentos para a categoria escolhida e oculta a original. Confirmação:
  "Mover {n} lançamentos de {A} para {B}?"
- Excluir só é oferecido para categoria sem nenhum lançamento.

## Seletor (usado nas outras telas)

Desktop: combobox com busca; resultado "Moradia › Aluguel". Mobile: lista com pais; tocar no pai abre as filhas, com
"Usar só {pai}" no topo.

## Dados

- Migração: `categories.parent_id` (nullable, FK para `categories`, `on_delete: :restrict`), `position` (integer),
  `merged_into_id` (nullable, FK). **"Ocultar" usa o `active` que já existe** (`scope :active`) — sem coluna nova.
- Validações no model:
  1. o pai precisa ser raiz (`parent.parent_id` nulo) — sem neta;
  2. **categoria com filhas não pode virar filha**;
  3. pai do mesmo usuário e do mesmo `category_type`; não pode ser pai de si mesma;
  4. a filha herda `natureza` e `category_type` do pai (atribuídos antes da validação; não editáveis na filha).
- `GET /categories` passa a devolver `parent_id`, `position`; filtros aceitam `include_children`.
- **Novo** `POST /categories/:id/merge` (`into_id`) — `CategoryMergeService`, tudo numa transação de banco:
  - move `transactions.category_id`;
  - move orçamentos; se o destino já tem orçamento no mesmo mês (índice único
    `user_id, category_id, period_year, period_month`), **soma os limites** no destino e apaga o da origem;
  - repassa `reimbursed_by_category_id` de quem apontava para a origem;
  - filhas da origem passam para o destino, se o destino for raiz; se o destino for filha e a origem tiver
    filhas, o merge é recusado (validação 2);
  - origem fica `active: false` com `merged_into_id` = destino;
  - `AutoCategorizerService` não guarda aprendizado (são regras fixas que acham a categoria **pelo nome**); passa a
    seguir `merged_into_id` quando a categoria encontrada estiver mesclada, para a regra continuar acertando;
  - quando existirem agendados (spec 06), o serviço também move `scheduled_transactions.category_id`.
- `DefaultCategoriesSeederService`: avaliar presets com subcategorias (inspirado no padrão de E1), em pt-BR, com
  categorias próprias.
- `natureza_split` soma filhas no pai (a natureza é herdada, então o split não muda).

## Orçamento com limite no pai e na filha (sem dupla contagem)

- Gasto do pai = lançamentos no pai + em todas as filhas. Gasto da filha = só os dela.
- O limite da filha é um **sub-envelope dentro** do pai; não soma ao total.
- Limite efetivo do grupo = limite do pai, se houver; senão, a soma dos limites das filhas.
- Total do mês = soma dos limites efetivos **por grupo** (cada pai entra uma vez). Gasto total = soma dos gastos dos
  grupos (cada lançamento conta uma vez).
- Soma dos limites das filhas maior que o limite do pai → aviso na tela de orçamento: "Os limites das subcategorias
  passam o da categoria." Não bloqueia.

## Critérios de aceite

1. Não dá para criar neta (validação de modelo + request spec).
2. Mesclar move lançamentos e orçamentos numa transação de banco; falha não deixa estado parcial.
3. Categoria inativa (oculta) não aparece no seletor, mas o lançamento antigo continua mostrando o nome.
4. Orçamento no pai soma as filhas (spec 05) e o total do mês é igual à soma dos lançamentos do mês — testado com:
   só pai; só filhas; pai + filhas com limite; lançamento direto no pai; filha sem limite com gasto.
5. Categoria com filhas não pode receber `parent_id` (model spec).
6. Merge com orçamento nos dois lados no mesmo mês soma os limites; `reimbursed_by_category_id` é repassado;
   falha forçada no último passo não deixa nada alterado (request spec).
7. Depois de mesclar "Alimentação" em outra categoria, uma descrição "supermercado" continua sendo categorizada — no
   destino.
