# Wealthfolio — relatório ação → reação

- Licença / classe (12): AGPL-3.0 · UX observável / caixa-preta
- Versão ou commit: binário local em execução; código não consultado
- Ambiente: servidor local isolado, porta 4102, dados sintéticos descartáveis
- Data: 2026-10-20
- Tarefas executadas / bloqueadas: W4 parcialmente executada; W1–W3 e W5 pendentes de ações sintéticas confirmadas.

| # | Estado inicial | Ação | Reação na tela | Reação nos dados (saldo, lista, orçamento) | Fonte | Regra extraída | Teste de aceite no Klipper |
|---|---|---|---|---|---|---|---|
| W4.1 | Painel com duas contas patrimoniais, R$ 15.000,00 e sem posições | Abrir o painel em 390 px | O painel preservou valor patrimonial, período, contas, holdings vazios e metas; a barra lateral virou navegação inferior com painel, insights, busca e mais opções. A área de patrimônio também apresentou decomposição e ritmo mensal sem depender de tabela de movimentos. | Nenhum dado foi alterado. | execução | Em mobile, leitura patrimonial pode manter prioridade no total e nos próximos passos, enquanto a navegação secundária reduz para poucos destinos. Isso não prova o fluxo de cadastro ou de atividade. | UXR-08: em 390 px, total patrimonial, período, conta e próxima ação são legíveis sem rolagem horizontal; a navegação não oculta atividades. |

## Lacunas

- W1: aporte, compra, venda e dividendo sintéticos; alteração do painel e transição de métricas indisponíveis.
- W2: validação e recuperação para atividade incompleta.
- W3: editar, excluir e desfazer atividade.
- W4: conta e formulário de atividade em 390 px.
- W5: importação e duplicata.
