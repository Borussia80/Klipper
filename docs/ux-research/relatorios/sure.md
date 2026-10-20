# Sure — relatório ação → reação

- Licença / classe (12): AGPL-3.0 · UX observável / caixa-preta
- Versão ou commit: imagem local em execução; código não consultado
- Ambiente: container local isolado, porta 4100, dados sintéticos descartáveis
- Data: 2026-10-20
- Tarefas executadas / bloqueadas: S1–S4 executadas parcialmente; S5 executada até a correção de erros. Não foi habilitada nem configurada a área de IA.

| # | Estado inicial | Ação | Reação na tela | Reação nos dados (saldo, lista, orçamento) | Fonte | Regra extraída | Teste de aceite no Klipper |
|---|---|---|---|---|---|---|---|
| S1 | Conta vazia em ambiente local | Criar conta manual com saldo inicial | O formulário concluiu e mostrou confirmação; a conta abriu no detalhe. A falha silenciosa previamente relatada não se repetiu nesta execução. | Conta apareceu na árvore, com saldo inicial e linha de histórico datada. | execução | A criação deve terminar em confirmação inequívoca e levar ao detalhe já consistente; uma falha anterior precisa de cenário reprodutível antes de ser tratada como regra do produto. | UXR-01: criar conta mostra sucesso, abre o detalhe e apresenta a linha de saldo inicial. |
| S2 | Uma conta sintética com saldo inicial | Abrir detalhe e criar despesa | A tela de detalhe mostrou saldo, variação no período, gráfico e atividade. Submissão sem descrição foi bloqueada junto ao campo; lançamento válido fechou o formulário. | Saldo caiu de R$ 2.500,00 para R$ 2.374,50 e surgiu uma linha de atividade sem categoria. | execução | Validação local deve apontar o campo antes da gravação; sucesso precisa atualizar saldo, evolução e histórico juntos. | UXR-01 e UXR-02: campo obrigatório recebe erro associado; lançamento confirmado atualiza lista, saldo e gráfico. |
| S3 | Despesa sintética criada | Editar nome e valor, fechar e reabrir | A edição não apresentou ação explícita de salvar; depois de reabrir, a lista refletiu nome e valor alterados. Não foi encontrada opção de desfazer. | Valor passou a R$ 130,00 e saldo a R$ 2.370,00. | execução | Se houver salvamento automático, a interface precisa comunicar seu estado e oferecer cancelamento/restauração; não se deve inferir desfazer sem evidência. | UXR-04: edição anuncia salvamento, permite cancelar antes da persistência e oferece retorno verificável após mutação. |
| S4.1 | Duas contas sintéticas: R$ 2.370,00 e R$ 1.000,00 | Criar transferência de R$ 200,00 | A transferência foi mostrada com origem, destino, data e duas pontas no detalhe/lista. | Saldos passaram a R$ 2.170,00 e R$ 1.200,00. | execução | Transferência deve exibir contrapartida e alterar os dois saldos de maneira rastreável. | UXR-03: criar transferência atualiza ambas as contas e exibe vínculo único entre as pontas. |
| S4.2 | Transferência criada | Abrir configurações e remover transferência | Houve explicação e confirmação. Após confirmar, o vínculo de transferência desapareceu. | As duas transações subjacentes e os saldos permaneceram; a origem continuou com -R$ 200,00 e o destino com +R$ 200,00. | execução | Remover somente o vínculo deixa dois movimentos financeiros sem contrapartida, situação que exige decisão explícita e opção de restauração/revinculação. | UXR-03 e UXR-04: exclusão de transferência explica o destino das pontas; o Klipper deve manter, reverter ou tornar revisáveis ambas de forma atômica. |
| S5 | CSV sintético de 13 linhas e importação sem gravação | Colar CSV, mapear data, valor, conta, nome e categoria, avançar para limpeza | Upload confirmou o recebimento. A etapa de limpeza marcou cada linha como inválida e revelou o motivo: as datas estavam além do limite aceito. A mudança de uma data para o período permitido não removeu o marcador imediatamente. | Nenhuma linha foi confirmada/importada; não houve reimportação. | execução | Importação precisa expor erro por linha, manter os dados editáveis e recalcular validação de forma perceptível após a correção. | UXR-06: arquivo com datas futuras mostra todas as linhas pendentes e, ao corrigir uma, atualiza o estado daquela linha sem reprocessar silenciosamente o arquivo. |

## Testes de aceite novos ou alterados por UXR

- UXR-01: uma conta criada manualmente tem sucesso visível, detalhe acessível e saldo inicial no histórico.
- UXR-03: remover uma transferência não pode deixar pontas órfãs sem decisão e trilha de recuperação.
- UXR-04: edição automática mostra estado de salvamento e oferece cancelamento ou restauração.
- UXR-06: erro de importação é localizado por linha e a correção muda claramente o estado de validação.

## Próxima rodada: dívida, cartão e financiamento

O estudo ainda não exercitou estes tipos de conta. A próxima execução deve criar cartão de crédito e financiamento sintéticos, registrar compra/fatura/pagamento e parcela/amortização, e conferir saldo, principal, juros, vencimento, transferência e erro de validação em desktop e 390 px.
