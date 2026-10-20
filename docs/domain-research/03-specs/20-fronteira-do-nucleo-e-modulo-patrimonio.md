# Spec 20 — Fronteira entre núcleo financeiro e módulo de patrimônio

**Status:** decisão de escopo — 2026-10-20.
**Objetivo:** entregar confiabilidade de caixa, dívida e importação antes de posições, cotações e performance.

## Núcleo obrigatório (P0)

O núcleo é autônomo e não depende de corretora, cotação, agregador ou valor de mercado. Ele entrega:

1. contas de ativo e passivo, saldo derivado e reconciliação (spec 02);
2. lançamento comum, split, estorno e transferência atômica (spec 03);
3. cartão, fatura, ciclo, vencimento e pagamento identificado (spec 04);
4. financiamento, parcela, juros, amortização e quitação (spec 19);
5. importação revisável, deduplicação, correção e desfazer (spec 06);
6. orçamento e projeção de caixa baseados nos lançamentos confirmados.

O patrimônio do núcleo é apenas a soma datada de saldos de contas ativas e passivas. Uma conta `investment` sem
módulo de investimentos entra por custo, com rótulo explícito `custo`; não inventa rentabilidade nem cotação.

## Módulo separado: patrimônio e investimentos

Investimentos é um módulo posterior, ativável sem reescrever o ledger. Ele pode adicionar:

- instrumento, posição, lote, aporte, venda, provento e evento corporativo;
- custo, valor de mercado, cotação, fonte, data e divergência de fontes;
- performance, benchmark, impostos e consolidação por classe de ativo.

As specs 11, 18 e a parte de investimentos do D9 são dependências desse módulo. Elas não bloqueiam D1–D8 nem
autorizam usar cotação externa no núcleo.

## Contrato de integração

1. Todo efeito de caixa de investimento gera movimento normal no núcleo: aporte e compra saem da conta pagadora;
   venda, dividendo e juros entram na conta recebedora. Esses movimentos preservam `origin_type` e `origin_id` para
   ligar ao módulo, sem mudar sua semântica de saldo.
2. A posição não é uma segunda conta corrente. Seu valor de custo ou mercado alimenta apenas a consulta patrimonial
   datada; nunca cria receita, despesa ou caixa automaticamente.
3. Falha, atraso ou ausência de cotação mantém o último valor conhecido com data/fonte, ou usa custo quando não
   houver mercado. Nunca altera movimentos financeiros já confirmados.
4. Desativar o módulo mantém lançamentos e conta de investimento; apenas remove métricas e dados derivados do
   módulo, sem apagar o histórico financeiro.

## Portas de implementação

O módulo só pode iniciar quando o núcleo passar os seguintes cenários de aceite:

| Cenário | Resultado obrigatório |
|---|---|
| Transferência criada, editada, falha, excluída e desfeita | Duas pontas, saldos e vínculo permanecem coerentes; não há ponta órfã. |
| Pagamento de cartão | Fatura, ciclo, vencimento, caixa e saldo devedor apontam para o mesmo resultado. |
| Parcela de financiamento | Juros, principal, saldo posterior e projeção reconciliam. |
| Importação | Prévia preserva origem e decisão; corrigir, reimportar e desfazer não duplicam nem perdem decisão. |
| Mobile e teclado | Jornadas críticas acima passam em 390 px e por teclado. |

## Decisão de interface

O painel inicial do núcleo prioriza caixa, dívidas, vencimentos e alertas. A seção `Patrimônio e investimentos`
entra como destino separado quando o módulo estiver disponível. Não haverá gráfico de performance vazio ou estimado
disfarçado de dado financeiro.
