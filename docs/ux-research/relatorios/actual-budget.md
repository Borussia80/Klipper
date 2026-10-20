# Actual Budget — relatório ação → reação

- Licença / classe (12): MIT · técnica/dados de execução
- Versão ou commit: `8fba0e87cf7a4cda6ab5ea8012477bd7051f6ebc` (MIT confirmado em `LICENSE.txt`)
- Ambiente: demonstração pública oficial, banco local no navegador
- Data: 2026-10-20
- Tarefas executadas / bloqueadas: A1 bloqueada na transferência do arquivo pelo navegador integrado

| # | Estado inicial | Ação | Reação na tela | Reação nos dados (saldo, lista, orçamento) | Fonte | Regra extraída | Teste de aceite no Klipper |
|---|---|---|---|---|---|---|---|
| A1.1 | Conta preenchida da demonstração pública | Abrir Importar e selecionar o CSV do Lote 0 | O botão abriu o fluxo de importação por arquivo, mas o seletor oculto do navegador integrado não emitiu a escolha, mesmo pelo controle nativo. | Nenhum dado da demonstração foi alterado; reimportação e confirmação não puderam ser executadas. | execução · demo pública | Bloqueado: o sandbox não disponibilizou a transferência do arquivo para a demonstração. Não há conclusão comportamental sobre duplicatas. | — |
| A1.2 | Fonte MIT local, sem execução do arquivo | Verificar o contrato técnico de importação | — | — | código · `packages/loot-core/src/types/models/import-transaction.ts@8fba0e8` | A importação pode carregar um identificador externo estável para impedir a repetição do mesmo movimento; sem esse identificador, a conclusão sobre equivalência por data, valor ou descrição exige execução posterior. | UXR-06: manter identificador de origem quando disponível e apresentar incerteza de duplicidade quando ele estiver ausente. |

## Testes de aceite novos ou alterados por UXR

- Nenhum teste fechado: a execução do CSV precisa ser repetida em servidor local oficial ou em navegador com upload funcional.
