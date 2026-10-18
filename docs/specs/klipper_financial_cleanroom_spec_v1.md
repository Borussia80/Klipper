# Especificação funcional clean-room — núcleo financeiro do Klipper

**Destinatário:** equipe/agente implementador sem acesso ao Sure ou ao relatório forense.  
**Objetivo:** implementar comportamento financeiro independente no Rails/Nuxt do Klipper.

## Requisitos de domínio

1. Cada conta pertence a exatamente um usuário e tem moeda, classificação de ativo/passivo e data de abertura.
2. Todo lançamento efetivo pertence a uma conta, possui data financeira, valor em unidade exata, moeda, direção de negócio e origem auditável.
3. Saldo em data `d` deve ser explicável por saldo inicial, movimentos efetivos até `d` e correções explícitas. O saldo atual cacheado nunca é a única fonte da história.
4. Uma correção de saldo deve ter data, motivo, usuário/origem e efeito rastreável. Correção em data antiga não pode sobrescrever silenciosamente o saldo atual.
5. Transferência é um grupo de duas pernas relacionadas em contas distintas. Em mesma moeda, valores algébricos se anulam. Transferência não é receita nem despesa.
6. Reversão é preferível à exclusão definitiva para fatos financeiros confirmados. Se exclusão for permitida, reprocessar saldos e conservar auditoria.
7. Split exige soma exata das partes igual ao valor do lançamento original; confirmar ou rejeitar deve ser atômico.
8. Patrimônio na data `d` é ativos avaliados em `d` menos passivos avaliados em `d`. Avaliação de investimento deve registrar data e moeda.
9. Importação bancária deve preservar identificador externo/origem e obedecer idempotência por conta e fonte.
10. Toda mutação e consulta deve respeitar usuário e autorização sobre a conta.

## Critérios de aceitação

- Inserir movimento retroativo recalcula saldos posteriores e o patrimônio afetado.
- Duas confirmações da mesma importação não criam dois lançamentos.
- Duas transações legítimas parecidas não são removidas só por valor/data próximos.
- Transferência para a própria conta é recusada; transferências em mesma moeda fecham em zero.
- Uma falha no meio de split ou transferência não persiste estado parcial.
- Saldo corrente, extrato e relatório histórico retornam números compatíveis para a mesma data.
- Alterar descrição/categoria sem efeito financeiro não exige recálculo de valor.
- Contas excluídas de relatórios não aparecem em totais novos; a regra histórica deve ser explícita e testada.
- Dado em outra conta/usuário não é legível, reconciliável ou atualizável.

## Casos sintéticos obrigatórios

1. Abertura BRL 1.000; débito BRL 120 em 05/01; saldo de 05/01 = BRL 880.
2. Inserir débito BRL 30 em 03/01 depois do cenário anterior; saldo de 05/01 = BRL 850.
3. Transferir BRL 100 de A para B: A reduz 100, B aumenta 100 e resultado mensal não muda.
4. Dividir débito 100 em 60 e 40; toda consulta totaliza 100 uma única vez.
5. Correção externa para saldo 870 em 05/01 deve permanecer auditável e não apagar lançamentos.
6. Duas compras de 50 no mesmo dia devem poder coexistir.
7. Importação externa repetida com mesmo ID confiável deve ser idempotente.
8. Valor em moeda estrangeira deve manter valor, moeda, taxa e data de taxa; não comparar nominalmente com outra moeda.

## Limites de implementação

- Não utilizar código, testes, fixtures, pseudocódigo, comentários ou estrutura interna de projetos AGPL como referência de implementação.
- Usar a arquitetura existente do Klipper: Rails, PostgreSQL, API JSON e Nuxt.
- Implementar em etapas, com testes próprios e dados sintéticos.
- Tratar valores monetários com `decimal` ou unidade menor inteira, nunca ponto flutuante.
