# Ghostfolio — relatório ação → reação

- Licença / classe (12): AGPL-3.0 · caixa-preta; contexto histórico marcado como *dirty* limitado somente para ambiente
- Versão ou commit: imagem local em execução; código não consultado nesta sessão
- Ambiente: servidor local isolado, porta 4103, dados sintéticos descartáveis
- Data: 2026-10-20
- Tarefas executadas / bloqueadas: G3 parcialmente executada no estado vazio; G1, G2 e G4 pendentes de ações sintéticas confirmadas.

| # | Estado inicial | Ação | Reação na tela | Reação nos dados (saldo, lista, orçamento) | Fonte | Regra extraída | Teste de aceite no Klipper |
|---|---|---|---|---|---|---|---|
| G3.1 | Onboarding sem contas nem atividades | Abrir painel em 390 px | O estado vazio manteve três passos ordenados — configurar contas, registrar atividades e acompanhar carteira — e uma ação para iniciar. A navegação principal recolheu os rótulos em controles compactos. | Nenhum dado foi alterado. | execução | Estado vazio orienta a primeira jornada, mas não deve simular patrimônio nem esconder qual é o próximo dado necessário. A responsividade observada não cobre contas, atividade ou erros. | UXR-10 e UXR-08: sem dados, o Klipper apresenta uma ação primária e passos compreensíveis; em 390 px, esses passos permanecem acessíveis sem conteúdo fictício. |
| G3.2 | Mesmo onboarding móvel | Percorrer o foco pelo teclado | A ordem de foco alcançou logo, controles e o link de configurar conta; o CTA expôs rótulo que descreve a ação e o resultado. | Nenhum dado foi alterado. | execução | Um estado vazio deve ter caminho de teclado e nome acessível para a próxima ação, mas um ensaio de onboarding não valida formulários, erro ou leitor de tela completo. | UXR-12: no estado vazio, Tab alcança o CTA principal com nome descritivo; login, lançamento, transferência e exclusão recebem ensaios equivalentes antes de encerrar acessibilidade. |

## Lacunas

- G1: criar, editar e excluir atividade, com efeito em conta e total.
- G2: recuperação com token e token inválido.
- G3: contas, atividades e painel preenchido em 390 px.
- G4: envio de atividade inválida e recuperação.
