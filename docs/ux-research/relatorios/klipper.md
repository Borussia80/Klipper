# Klipper — relatório ação → reação

- Licença / classe (12): aplicação própria do Klipper; observação local, sem análise de código.
- Versão ou commit: não obtido; o alfa local não respondeu.
- Ambiente: `http://localhost:3000`, largura prevista 390 px.
- Data: 2026-11-19.
- Tarefas executadas / bloqueadas: M7 bloqueada antes da interação porque a conexão local foi recusada.

## Protocolo

O request para `http://localhost:3000` retornou falha de conexão. Conforme a condição da tarefa, o alfa não foi iniciado. Nenhum dado sintético foi criado; não houve navegação de interface, captura ou leitura de código. Toques, duração, erros de fluxo e foco não foram medidos.

| # | Estado inicial | Ação | Reação na tela | Reação nos dados | Fonte | Regra extraída | Teste de aceite no Klipper |
|---|---|---|---|---|---|---|---|
| M7.1 | bloqueado: alfa local ausente em `localhost:3000` | Verificar navegação inferior | bloqueado: sem servidor | não observado | execução bloqueada | — | — |
| M7.2 | bloqueado: alfa local ausente em `localhost:3000` | Abrir `+`, criar movimento sintético e consultar lista | bloqueado: sem servidor | nenhum dado criado | execução bloqueada | — | — |
| M7.3 | bloqueado: alfa local ausente em `localhost:3000` | Observar estado de erro de rede | bloqueado: sem servidor | erro de fluxo não provocado | execução bloqueada | — | — |

UXR afetados: UXR-01, UXR-07, UXR-08, UXR-10 e UXR-12. Sem reação nova para atualizar a matriz 11. Não há prints porque nenhuma tela carregou.
