# Actual Budget — relatório ação → reação

- Licença / classe (12): MIT · técnica/dados de execução
- Versão ou commit: `8fba0e87cf7a4cda6ab5ea8012477bd7051f6ebc` (MIT confirmado em `LICENSE.txt`)
- Ambiente: servidor oficial local, porta 4105, orçamento de demonstração descartável
- Data: 2026-10-20
- Tarefas executadas / bloqueadas: A1 executada

| # | Estado inicial | Ação | Reação na tela | Reação nos dados (saldo, lista, orçamento) | Fonte | Regra extraída | Teste de aceite no Klipper |
|---|---|---|---|---|---|---|---|
| A1.1 | Conta preenchida do orçamento de demonstração local | Enviar o CSV e escolher o formato de data ISO | A prévia mostrou 13 linhas, mapeou data, descrição, categoria e valor; a coluna `account` foi tratada como nota e os campos de tipo/destino não entraram na importação. | A primeira confirmação inseriu 13 movimentos sem categoria e alterou o saldo da conta. | execução · servidor local | Uma importação deve revelar o mapeamento efetivo antes de gravar e tornar lacunas de categoria e transferência explícitas, sem reinterpretar silenciosamente as colunas. | UXR-06: prévia permite corrigir ou ignorar cada coluna não suportada e identifica lançamentos que não serão tratados como transferência. |
| A1.2 | Mesmo arquivo após a primeira importação, opção de mesclar ativa | Reimportar o CSV | As 13 linhas voltaram na prévia, todas desmarcadas; isso incluiu as duas iguais e a quase duplicata com descrição diferente. O botão de importar ficou em zero. | Nenhum movimento adicional foi criado na segunda tentativa. | execução | Com a mesclagem ativa, o produto considera suficientes a proximidade temporal e o valor para evitar repetir uma linha; a descrição não impede a detecção da quase duplicata. A pessoa ainda pode revisar a seleção antes da ação. | UXR-06: mostrar por que uma linha é provável duplicata, com data, valor, conta e descrição; permitir importar mesmo assim por escolha explícita. |
| A1.3 | Fonte MIT local e execução concluída | Verificar o contrato técnico de importação | — | — | código · `packages/loot-core/src/types/models/import-transaction.ts@8fba0e8` | Um identificador externo estável aumenta a segurança da deduplicação quando o extrato o fornece; sem ele, a correspondência observada deve permanecer explicável e reversível. | UXR-06: conservar identificador de origem quando houver e registrar a base da correspondência quando não houver. |

## Testes de aceite novos ou alterados por UXR

- UXR-06: reimportar arquivo com duplicata exata e quase duplicata não cria novas linhas; a interface explica a correspondência e deixa a decisão de exceção para a pessoa.
- UXR-06: uma coluna sem semântica compatível não é descartada silenciosamente; a prévia a sinaliza antes da confirmação.
