# Spec 02 — Lançamento rápido

**Onde:** botão "+" global (mobile: centro da navegação inferior; desktop: atalho `N` e item "Criar" da barra
lateral, que já existem). · **Prioridade:** 1 · **Referências:** fluxo C1, avaliador de expressão E5, seletor de
categoria E1.

## Objetivo

Registrar um gasto comum em **até 4 toques** depois do "+": valor → categoria → salvar (conta e data com padrão).

## Mobile — folha inferior (ocupa ~85 % da altura)

```
┌──────────────────────────────────┐
│ [Saída] [Entrada]       ✕        │  segmento; padrão Saída
│                                  │
│          R$ 23,50                │  valor grande, alinhado à direita do centro
│  Mercado (descrição, opcional)   │
├──────────────────────────────────┤
│ Categoria: grade 4×2 das 8 mais  │  ícone neutro + nome; "Outras…" abre lista
│ usadas nos últimos 60 dias       │  em dois níveis (spec 07)
├──────────────────────────────────┤
│ Conta ▾  · Hoje ▾ · Portador ▾   │  chips com padrão; toque abre seletor
├──────────────────────────────────┤
│  7   8   9   ÷                    │
│  4   5   6   ×                    │  teclado próprio (sem abrir o do sistema)
│  1   2   3   −                    │
│  ,   0   ⌫   +                    │
│ [        Salvar        ]          │  44 px+, cor de ação
└──────────────────────────────────┘
```

- Abre com foco no valor e teclado próprio visível.
- Operadores calculam: `45,90+12` mostra "= R$ 57,90" em `--t3` abaixo do valor; salvar usa o resultado.
- Tocar na descrição abre o teclado do sistema; ao digitar, sugere categoria pelo título (mesma lógica do
  `AutoCategorizerService` — expor endpoint de sugestão, ver plano). Sugestão aparece pré-selecionada na grade com
  rótulo "sugerida".
- Conta padrão: a última usada neste aparelho; data padrão: hoje; portador padrão: titular.
- Arrastar a folha para baixo fecha; se houver valor digitado, pergunta "Descartar este lançamento?".

## Desktop — o modal atual reorganizado

Mesmo `BaseModal`, mesma ordem lógica: tipo → valor (campo com expressão) → descrição → categoria (combobox com
busca, mostra "Pai › Filha") → conta → data → portador → parcelas (recolhido) → observação (recolhido).
`Enter` salva; `Ctrl+Enter` salva e abre outro em branco.

## Dados

`POST /transactions` com `amount`, `transaction_type`, `occurred_on`, `description`, `category_id`, `account_id`,
`member_id` (já existe). Categorias mais usadas: **novo** `GET /categories?sort=usage&limit=8` ou cálculo no
cliente a partir das transações em cache — preferir o endpoint.

## Validação e estados

| Situação | Comportamento |
|---|---|
| Valor zero ou vazio | Salvar desabilitado; texto: "Informe um valor." |
| Expressão inválida (`12++`) | Mostra "Conta incompleta" no lugar do resultado; salvar desabilitado |
| Sem categoria | Permitido — vai como "sem categoria" e entra no `data_health` |
| Salvando | Botão com indicador, folha travada |
| Sucesso | Folha fecha; toast transitório `--ok`: "Lançamento salvo." + [Desfazer] por 5 s |
| Erro de rede | Folha continua aberta com os dados; faixa crítica: "Não foi possível salvar. Seus dados continuam aqui." [Tentar de novo] |
| 401 | Renovação transparente (regra existente do projeto), sem perder o formulário |

## Campo de valor: expressão, ponto e vírgula

Calculado por `utils/amountExpression.ts` (porte do avaliador do ezBookkeeping — tokenizador + notação pós-fixa).
**Sem `eval` e sem `new Function`.**

Cada número da expressão é normalizado antes do cálculo:

- **Tem vírgula:** a vírgula é o decimal; pontos são separador de milhar e precisam estar em grupos de 3 dígitos
  (`1.234,56`), senão a expressão é inválida.
- **Não tem vírgula:** um ponto seguido de **exatamente 3 dígitos** no fim é milhar (`1.500` = 1500, como se escreve
  no Brasil); qualquer outro ponto é decimal (`1.5` = 1,5, teclado do celular em inglês).
- Mais de um separador decimal no mesmo número é inválido.
- Resultado arredondado a 2 casas (meio para cima) e guardado em **centavos inteiros**, para não acumular erro de
  ponto flutuante.

| Entrada | Resultado |
|---|---|
| `1.234,56` | 1.234,56 |
| `1.5` | 1,50 |
| `10+2,5` | 12,50 |
| `1.500` | 1.500,00 |
| `1.234.567,8` | 1.234.567,80 |
| `45,90+12` | 57,90 |
| `-5+10` | 5,00 |
| `1,2,3` · `1.23,4` · `12++` · `10/0` | inválido |
| resultado ≤ 0 | não salva |
| acima do limite máximo | inválido |

## Critérios de aceite

1. Do "+" ao salvo, com conta e data padrão, gasto com categoria da grade: 4 toques (valor conta como 1 sequência).
2. Todos os casos da tabela acima passam, e o arquivo não contém `eval(` nem `new Function` (teste).
3. Desfazer remove o lançamento criado (DELETE) e mostra "Lançamento removido."
4. Em 390 px, teclado próprio e botão salvar visíveis sem rolar.
5. Testes: unidade do avaliador (portado — ver plano), componente da folha (padrões, validação, desfazer).
