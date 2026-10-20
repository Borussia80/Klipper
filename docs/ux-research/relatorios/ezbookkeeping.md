# ezBookkeeping — relatório ação → reação

- Licença / classe (12): MIT · técnica/dados de execução
- Versão ou commit: `3dcc316e1fb6a190d6a0dd13fbe4052d17b9315c` (MIT confirmado em `LICENSE`)
- Ambiente: container local, porta 4101
- Data: 2026-10-20
- Tarefas executadas / bloqueadas: E1 executada

| # | Estado inicial | Ação | Reação na tela | Reação nos dados (saldo, lista, orçamento) | Fonte | Regra extraída | Teste de aceite no Klipper |
|---|---|---|---|---|---|---|---|
| E1.1 | Conta local com saldo inicial em 19/10 e assistente aberto | Selecionar CSV, formato DSV/CSV e método de mapeamento | O assistente expõe quatro etapas: envio, mapeamento, revisão e conclusão. O input oculto não aceitou arquivo pelo navegador integrado; a API local do produto permitiu o mesmo fluxo. | A análise retornou 13 linhas; a linha sem categoria ficou pendente e a transferência exigiu conta de destino. | execução · API local | Importação precisa separar leitura, mapeamento e revisão; pendências não devem virar lançamento silencioso. | UXR-06: o CSV mostra cada linha e seu motivo de pendência antes de concluir. |
| E1.2 | CSV com conta/categorias ausentes e datas anteriores ao saldo inicial | Tentar concluir e corrigir as pendências | Houve erros específicos para conta de destino, categoria ausente e data anterior ao saldo inicial. Após criar dados sintéticos faltantes, escolher categoria para a linha vazia e usar data posterior ao saldo inicial, a conclusão informou 13/13. | Foram inseridos 13 movimentos sintéticos, inclusive transferência entre as duas contas de teste. | execução | Erro de importação deve apontar o campo recuperável e preservar a revisão para correção, sem importação parcial opaca. | UXR-01/06: cada erro de conta, categoria ou data oferece correção por linha e a conclusão informa inseridos, pendentes e descartados. |
| E1.3 | 13 movimentos importados | Reimportar o mesmo CSV com nova sessão de envio | A conclusão voltou a informar 13/13; não houve alerta nem escolha para duplicatas exatas ou quase duplicata. | A segunda importação criou outra cópia das 13 linhas. | execução + código · `pkg/api/transactions.go@3dcc316` | A proteção observada evita repetir a mesma submissão técnica; ela não compara conteúdo de arquivos importados. Portanto, descrição alterada, valor/data iguais e duplicatas exatas seguem para inserção numa nova importação. | UXR-06: duplicatas exatas e prováveis recebem estado visível, explicação dos campos coincidentes e decisão explícita de importar, mesclar ou ignorar; nunca são inseridas silenciosamente. |

## Testes de aceite novos ou alterados por UXR

- UXR-06: reimportar o arquivo com duas linhas iguais e uma quase igual deve manter todas revisáveis, com distinção entre coincidência exata e provável.
- UXR-01: falhas de conta, categoria e data devem ser recuperáveis no próprio lote, sem apagar o mapeamento já feito.
