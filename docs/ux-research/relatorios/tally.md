# Tally — relatório ação → reação

- Licença / classe (12): MIT; leitura técnica separada de UX observável.
- Versão ou commit: Tally 1.5.1, `9fa59f674605c164cd9b4db6be2ad3bf6313df04`.
- Ambiente: `app/src/main/assets` servido em `http://127.0.0.1:4178/`; `index.html` respondeu HTTP 200. Acesso à automação de navegador indisponível.
- Data: 2026-11-19.
- Tarefas executadas / bloqueadas: pinagem e confirmação do `LICENSE`; servidor estático iniciado, verificado e encerrado. Observação visual de M2 bloqueada. Widget bloqueado: só existe no APK.

## Protocolo e dados

Largura prevista: 390 px. Estado de navegador antes das tarefas: não acessível; a ferramenta CUA retornou `The browser access host is unavailable` e nenhuma aba ou aplicativo estava disponível. O servidor estático local foi verificado por HTTP, mas não houve inspeção visual. Nenhum dado foi criado, editado ou excluído. Toques, duração, erros de interação e foco não foram medidos. Não há prints de M2 porque nenhuma reação de interface pôde ser observada.

## Ação → reação

| # | Estado inicial | Ação | Reação na tela | Reação nos dados | Fonte | Regra extraída | Teste de aceite no Klipper |
|---|---|---|---|---|---|---|---|
| M2.1 — valor/calculadora | bloqueado: navegador indisponível | Abrir em 390 px e inserir valor sintético usando a calculadora | bloqueado: não foi possível abrir o navegador | não observado; nenhum dado inserido | execução bloqueada; assets MIT fixados abaixo | nenhuma conclusão de UX | — |
| M2.2 — grade de categorias | bloqueado: navegador indisponível | Abrir e selecionar uma categoria sintética | bloqueado: não foi possível abrir o navegador | não observado; nenhum dado inserido | execução bloqueada | nenhuma conclusão de UX | — |
| M2.3 — excluir/desfazer | bloqueado: navegador indisponível | Excluir e procurar desfazer em dado sintético | bloqueado: não foi possível abrir o navegador | não observado; nenhum dado excluído | execução bloqueada | nenhuma conclusão de UX | — |
| M2.4 — empréstimo/a receber | bloqueado: navegador indisponível | Criar cenário sintético de empréstimo e recebimento | bloqueado: não foi possível abrir o navegador | não observado; nenhum dado criado | execução bloqueada | nenhuma conclusão de UX | — |
| M2.W — widget | widget restrito ao APK | Observar o widget | bloqueado: o widget só existe no APK e não está nos assets servidos | não observado | bloqueio de escopo | nenhuma conclusão de UX | — |

## Análise técnica MIT — não é observação de comportamento

O repositório oficial declara MIT no `LICENSE` do commit registrado no cabeçalho. Foram consultados `app/src/main/assets/index.html`, `calculator.js`, `state.js`, `loans.js` e `bridge.js`. A leitura indica componentes de entrada numérica com calculadora; uma rotina local de desfazer que guarda cópias do estado financeiro; tratamento técnico de empréstimo e valores recebidos; e uma integração de widget ligada à ponte Android. Essas constatações descrevem o código, não a reação da interface nem o efeito observado em dados. Nenhum código, CSS, asset ou texto de interface foi copiado para o Klipper.

## Interface reaproveitável × regras financeiras próprias do Klipper

Nenhum padrão de interface foi classificado como reaproveitável: calculadora, grade, exclusão, desfazer e empréstimo ficaram sem observação visual neste lote. A leitura técnica isolada não preenche essa lacuna.

| Regra do Klipper que não é importada do Tally | Regra própria a preservar |
|---|---|
| K-15a — mês de contabilização do cartão | Usar o mês do vencimento da fatura e preservar a data original da compra. Fonte própria: `docs/domain-research/03-specs/04-cartao-de-credito.md`. |
| K-5 — compra no fechamento | Compra no dia do fechamento pertence à fatura seguinte. Fonte própria: `docs/domain-research/03-specs/04-cartao-de-credito.md`. |
| K-4 — vencimento não útil | Deslocar o vencimento para o próximo dia útil. Fonte própria: `docs/domain-research/03-specs/04-cartao-de-credito.md`. |
| K-14 — parcelas | A primeira parcela é efetivada na fatura da compra; as seguintes ficam previstas nas faturas posteriores, mantendo a data original da compra. Fonte própria: `docs/domain-research/03-specs/04-cartao-de-credito.md`. |

## Fechamento

UXR afetados: UXR-04, UXR-07 e UXR-09, sem atualização da matriz 11 porque nenhuma reação foi observada. Impressões: nenhum arquivo visual foi produzido; as tarefas bloqueadas estão identificadas pelos IDs acima. Fontes e proveniência também constam em `07-registro-pi.md` e `12-protocolo-de-proveniencia-e-clean-room.md`.
