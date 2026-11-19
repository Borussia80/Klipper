# Firefly III — relatório ação → reação

- Licença / classe (12): AGPL-3.0 · UX observável / caixa-preta, conforme roteiro do lote.
- Versão ou commit: não observado.
- Ambiente: servidor local previsto na porta 4104 sem resposta; demo pública não observável sem navegador.
- Data: 2026-10-31.
- Tarefas executadas / bloqueadas: F2.1–F2.4 e F6.1–F6.3 bloqueadas.
- Instrumentação: Playwright MCP e navegador manual indisponíveis; axe não executado.

Nenhum dado de laboratório foi criado. Não há capturas nem saldos observados. Nenhum código, CSS, template, migration, configuração ou documentação técnica interna do Firefly foi aberto.

| # | Estado inicial | Ação | Reação na tela | Reação nos dados (saldo, lista, orçamento) | Fonte | Regra extraída | Teste de aceite no Klipper |
|---|---|---|---|---|---|---|---|
| F2.1 | Não obtido | Criar transferência sintética | bloqueado: navegador indisponível; servidor local 4104 sem resposta; demo não observável | Saldos e orçamento não observados | — | — | — |
| F2.2 | Não obtido | Editar o valor | bloqueado: navegador indisponível; servidor local 4104 sem resposta; demo não observável | Saldos e orçamento não observados | — | — | — |
| F2.3 | Não obtido | Tentar editar uma ponta | bloqueado: navegador indisponível; servidor local 4104 sem resposta; demo não observável | Saldos e orçamento não observados | — | — | — |
| F2.4 | Não obtido | Excluir a transferência | bloqueado: navegador indisponível; servidor local 4104 sem resposta; demo não observável | Saldos e orçamento não observados | — | — | — |
| F6.1 | Não obtido | Excluir despesa em 1440 px | bloqueado: navegador indisponível; servidor local 4104 sem resposta; demo não observável | Saldos e orçamento não observados | — | — | — |
| F6.2 | Não obtido | Procurar recuperação em 1440 px | bloqueado: navegador indisponível; servidor local 4104 sem resposta; demo não observável | Saldos e orçamento não observados | — | — | — |
| F6.3.1 | Não obtido | Excluir despesa em 390 px | bloqueado: navegador indisponível; servidor local 4104 sem resposta; demo não observável | Saldos e orçamento não observados | — | — | — |
| F6.3.2 | Não obtido | Procurar recuperação em 390 px | bloqueado: navegador indisponível; servidor local 4104 sem resposta; demo não observável | Saldos e orçamento não observados | — | — | — |

## Lote mobile M5 — 2026-11-19

- Ambiente previsto: demonstração pública oficial. Nenhum login ou dado real foi usado.
- Larguras: 390 px conforme M5; 1440 px conforme o F6 marcado como mobile no doc 13.
- Bloqueio desta sessão: ferramenta de navegador indisponível (`The browser access host is unavailable`); a demonstração não foi aberta.
- Nenhuma despesa sintética foi excluída; sem saldos, listas, duração, toques, erros, foco ou prints observados. Nenhum código/CSS/configuração foi consultado.

| # | Estado inicial | Ação | Reação na tela | Reação nos dados | Fonte | Regra extraída | Teste de aceite no Klipper |
|---|---|---|---|---|---|---|---|
| M5.1 / F6.3 — 390 px | bloqueado: demo não aberta | Excluir despesa sintética | bloqueado: navegador indisponível | saldo e lista não observados | execução bloqueada | — | — |
| M5.2 / F6.3 — 390 px | bloqueado: exclusão não executada | Procurar recuperação/desfazer | bloqueado: navegador indisponível | restauração não observada | execução bloqueada | — | — |
| M5.3 / F6 — 1440 px | bloqueado: demo não aberta | Excluir despesa sintética e procurar recuperação | bloqueado: navegador indisponível | saldo, lista e restauração não observados | execução bloqueada | — | — |

UXR afetados: UXR-04 e UXR-08. Sem reação nova para a matriz 11; esta sessão confirma o bloqueio atual, não substitui nem reinterpreta as tentativas bloqueadas anteriores.

## Testes de aceite novos ou alterados por UXR

Nenhum: não houve observação nova. As células da matriz permanecem inalteradas.
