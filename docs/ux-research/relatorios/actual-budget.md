# Actual Budget — relatório ação → reação

- Licença / classe (12): MIT · técnica/dados de execução
- Versão ou commit: `8fba0e87cf7a4cda6ab5ea8012477bd7051f6ebc` (MIT confirmado em `LICENSE.txt`)
- Ambiente: servidor oficial local, porta 4105, orçamento de demonstração descartável
- Data: 2026-10-20
- Tarefas executadas / bloqueadas: A1, A2.1, A3.1 e A3.2 executadas; edição e desfazer explícito ainda pendentes

| # | Estado inicial | Ação | Reação na tela | Reação nos dados (saldo, lista, orçamento) | Fonte | Regra extraída | Teste de aceite no Klipper |
|---|---|---|---|---|---|---|---|
| A1.1 | Conta preenchida do orçamento de demonstração local | Enviar o CSV e escolher o formato de data ISO | A prévia mostrou 13 linhas, mapeou data, descrição, categoria e valor; a coluna `account` foi tratada como nota e os campos de tipo/destino não entraram na importação. | A primeira confirmação inseriu 13 movimentos sem categoria e alterou o saldo da conta. | execução · servidor local | Uma importação deve revelar o mapeamento efetivo antes de gravar e tornar lacunas de categoria e transferência explícitas, sem reinterpretar silenciosamente as colunas. | UXR-06: prévia permite corrigir ou ignorar cada coluna não suportada e identifica lançamentos que não serão tratados como transferência. |
| A1.2 | Mesmo arquivo após a primeira importação, opção de mesclar ativa | Reimportar o CSV | As 13 linhas voltaram na prévia, todas desmarcadas; isso incluiu as duas iguais e a quase duplicata com descrição diferente. O botão de importar ficou em zero. | Nenhum movimento adicional foi criado na segunda tentativa. | execução | Com a mesclagem ativa, o produto considera suficientes a proximidade temporal e o valor para evitar repetir uma linha; a descrição não impede a detecção da quase duplicata. A pessoa ainda pode revisar a seleção antes da ação. | UXR-06: mostrar por que uma linha é provável duplicata, com data, valor, conta e descrição; permitir importar mesmo assim por escolha explícita. |
| A1.3 | Fonte MIT local e execução concluída | Verificar o contrato técnico de importação | — | — | código · `packages/loot-core/src/types/models/import-transaction.ts@8fba0e8` | Um identificador externo estável aumenta a segurança da deduplicação quando o extrato o fornece; sem ele, a correspondência observada deve permanecer explicável e reversível. | UXR-06: conservar identificador de origem quando houver e registrar a base da correspondência quando não houver. |
| A2.1 | Conta de demonstração local com saldo R$ 6.249,13 | Criar despesa categorizada de R$ 12,34 | A linha entrou na lista no mesmo dia; a superfície observada não ofereceu confirmação explícita de desfazer. Uma tentativa de atalho de teclado não reverteu a inclusão enquanto a linha estava em edição. | Conta e total dentro do orçamento caíram R$ 12,34, para R$ 6.236,79 e R$ 9.958,11. | execução · servidor local | Um lançamento confirmado deve atualizar conta e orçamento de forma coerente. A ausência de desfazer visível não prova que não exista outra rota. | UXR-04: ao alterar ou excluir movimento, o Klipper anuncia desfazer com escopo e duração; conta e orçamento voltam juntos ao estado anterior. |
| A3.1 | Bank of America R$ 6.236,79 e Ally Savings R$ 3.943,53 | Criar transferência de R$ 10,00 para Ally Savings | O formulário trocou categoria por `Transferência`; o destino exibiu uma linha vinculada, com ação para abrir a conta de transferência. | Origem caiu para R$ 6.226,79 e destino subiu para R$ 3.953,53; o total consolidado não mudou. | execução · servidor local | A criação de transferência precisa produzir duas pontas reconhecíveis e preservar o patrimônio total. Edição, exclusão e desfazer ainda precisam de ensaio próprio. | UXR-03: criação mostra destino/origem e atualiza ambas as contas atomicamente; editar ou desfazer mantém o mesmo vínculo. |
| A3.2 | Transferência A3.1 vinculada e visível na conta de destino | Selecionar a linha, abrir ações e confirmar `Excluir` | O menu indicou que havia uma transação selecionada, pediu confirmação de exclusão e não mostrou opção de desfazer após concluir. | A linha sumiu da conta de destino, seu saldo voltou para R$ 3.943,53 e a conta de origem voltou para R$ 6.236,79; o total consolidado continuou inalterado. | execução · servidor local | A exclusão da ponta de destino propagou-se para a origem, preservando a integridade da transferência. A recuperação não foi oferecida como ação posterior observável. | UXR-03 e UXR-04: exclusão de transferência deve explicar que afeta as duas pontas e disponibilizar desfazer temporal; o restauro precisa recompor ambas sem duplicar saldo. |

## Testes de aceite novos ou alterados por UXR

- UXR-06: reimportar arquivo com duplicata exata e quase duplicata não cria novas linhas; a interface explica a correspondência e deixa a decisão de exceção para a pessoa.
- UXR-06: uma coluna sem semântica compatível não é descartada silenciosamente; a prévia a sinaliza antes da confirmação.


## Lote 1 — 2026-10-31

- Instrumentação: Playwright MCP e navegador manual indisponíveis; axe não executado.
- Ambiente: servidor local 4105 não respondeu; demo pública não observada por falta de navegador.
- Nenhum dado de laboratório foi criado; não há capturas nem saldos observados nesta sessão.
- Fonte técnica: Actual Budget, licença MIT confirmada no arquivo LICENSE.txt, commit `8fba0e87cf7a4cda6ab5ea8012477bd7051f6ebc`. Nenhum código foi copiado.

| # | Estado inicial | Ação | Reação na tela | Reação nos dados (saldo, lista, orçamento) | Fonte | Regra extraída | Teste de aceite no Klipper |
|---|---|---|---|---|---|---|---|
| A2.2 | Não obtido | Excluir despesa | bloqueado: navegador indisponível; servidor local 4105 sem resposta; demo não observável nesta sessão | Saldos e lista não observados | — | — | — |
| A2.3 | Não obtido | Desfazer exclusão | bloqueado: navegador indisponível; servidor local 4105 sem resposta; demo não observável nesta sessão | Saldos e lista não observados | — | — | — |
| A2.4 | Não obtido | Editar valor | bloqueado: navegador indisponível; servidor local 4105 sem resposta; demo não observável nesta sessão | Saldos e lista não observados | — | — | — |
| A2.5 | Não obtido | Desfazer edição | bloqueado: navegador indisponível; servidor local 4105 sem resposta; demo não observável nesta sessão | Saldos e lista não observados | — | — | — |
| A2.6 | Não obtido | Desfazer duas alterações | bloqueado: navegador indisponível; servidor local 4105 sem resposta; demo não observável nesta sessão | Saldos e lista não observados | — | — | — |
| A2.7 | Não obtido | Recarregar e tentar desfazer | bloqueado: navegador indisponível; servidor local 4105 sem resposta; demo não observável nesta sessão | Saldos e lista não observados | — | — | — |
| A3.3 | Não obtido | Criar transferência | bloqueado: navegador indisponível; servidor local 4105 sem resposta; demo não observável nesta sessão | Saldos e lista não observados | — | — | — |
| A3.4 | Não obtido | Editar valor na ponta de destino | bloqueado: navegador indisponível; servidor local 4105 sem resposta; demo não observável nesta sessão | Saldos e lista não observados | — | — | — |
| A3.5 | Não obtido | Editar data na origem | bloqueado: navegador indisponível; servidor local 4105 sem resposta; demo não observável nesta sessão | Saldos e lista não observados | — | — | — |
| A3.6 | Não obtido | Excluir pela ponta de destino | bloqueado: navegador indisponível; servidor local 4105 sem resposta; demo não observável nesta sessão | Saldos e lista não observados | — | — | — |
| A3.7 | Não obtido | Desfazer exclusão | bloqueado: navegador indisponível; servidor local 4105 sem resposta; demo não observável nesta sessão | Saldos e lista não observados | — | — | — |
| A2.C1 | Leitura técnica; sem execução | Examinar recuperação | — | Saldos não observados | código · `packages/loot-core/src/server/undo.ts@8fba0e8`, `packages/loot-core/src/platform/client/undo/index.ts@8fba0e8` e `packages/desktop-client/src/undo/index.ts@8fba0e8` | O histórico em memória agrupa alterações e conserva valores anteriores para revertê-las; há limite nominal de 20 grupos. A leitura não comprova o que acontece ao recarregar a página ou reiniciar o processo. | UXR-04: desfazer uma exclusão recompõe movimento, saldo e orçamento; verificar também o comportamento após recarga. |
| A3.C1 | Leitura técnica; sem execução | Examinar contrapartida | — | Saldos não observados | código · `packages/loot-core/src/server/transactions/transfer.ts@8fba0e8`, `packages/loot-core/src/server/transactions/index.ts@8fba0e8`, `packages/loot-core/src/server/transactions/app.ts@8fba0e8` e `packages/loot-core/src/shared/transfer.ts@8fba0e8` | A criação vincula as pontas e a atualização examinada propaga o valor com sinal oposto. A leitura realizada não comprova atomicidade da gravação nem propagação de data em todos os fluxos. | UXR-03: alteração e exclusão mantêm as pontas coerentes; falha intermediária não deixa saldo parcial ou vínculo órfão. |

### Testes de aceite novos ou alterados por UXR — lote 1

- UXR-03: verificar edição pelas duas pontas, falha intermediária e recomposição do par.
- UXR-04: verificar duas ações desfeitas em ordem e o comportamento após recarga, sem presumir o resultado do Actual.

A leitura de código não altera as células O/P/N da matriz; todas as ações de interface permanecem bloqueadas.
