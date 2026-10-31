# 12 — Protocolo de proveniência, pesquisa técnica e clean room

**Status:** controle de processo — 2026-10-20  
**Objetivo:** permitir pesquisa responsável de referências livres sem confundir observação de produto, análise de código e implementação do Klipper.

Este documento descreve um procedimento de engenharia e rastreabilidade; não é parecer jurídico. Licença, atribuição e compatibilidade de qualquer reuso literal continuam exigindo revisão específica antes de distribuição.

## Classificação das fontes

| Classe | O que pode entrar no dossiê | O que não pode seguir para implementação autoral | Uso permitido no Klipper |
|---|---|---|---|
| **UX observável** | fluxos, estados, mensagens resumidas, medidas de tarefa, falhas, requisitos neutros | texto de interface, layout distintivo, ícones, assets ou código | gerar requisito funcional próprio |
| **Técnica / dirty** | licença, versão, objetivo da leitura, comportamento técnico e conclusão funcional | código, nomes internos, estruturas de arquivo, schema, comentários, algoritmos e testes da fonte | análise, interoperabilidade ou uma especificação funcional revisada por equipe/contexto separado |
| **Reuso autorizado** | componente e licença, aviso de copyright, obrigação de redistribuição e decisão registrada | nada além do que a licença autorizar | incorporar somente após revisão explícita de licença e atribuição |

## Estado das referências desta pesquisa

| Referência | Classe atual | Limite operacional |
|---|---|---|
| Sure | UX observável | código não lido nesta pesquisa |
| Cashew | UX observável | código não lido nesta pesquisa |
| ezBookkeeping | técnica / MIT | leitura histórica registrada; qualquer reuso literal exige atribuição e revisão de compatibilidade |
| Firefly III | UX observável | demonstração usada sem código nesta pesquisa |
| Actual Budget | técnica / MIT | Leituras técnicas de importação, desfazer e transferência no commit `8fba0e87cf7a4cda6ab5ea8012477bd7051f6ebc`; execução visual do lote 1 bloqueada. Fontes e histórico em `07-registro-pi.md`; não houve cópia |
| Wealthfolio | UX observável | binário executado; código não lido nesta pesquisa |
| Ghostfolio | técnica / AGPL-3.0, limitada | configuração distribuída foi inspecionada para configurar Redis; este contexto não é clean para implementar a partir de análise técnica do Ghostfolio |

## Fluxo obrigatório para uma análise técnica

1. Declarar a pergunta técnica concreta antes de abrir código, por exemplo: “qual contrato de dados preciso interoperar?”
2. Registrar repositório, versão/commit, licença, arquivos ou documentação consultados e conclusão em um dossiê da referência.
3. Produzir uma especificação funcional neutra: comportamento esperado, entradas, saídas, invariantes, estados de erro e critérios de aceite. Ela não deve carregar nomes internos, trechos, esquemas, estrutura de arquivos ou comentários da fonte.
4. Marcar a fonte e o contexto que a leu como **técnica/dirty**.
5. Se o Klipper precisar de implementação independente com alegação de clean room, entregar somente a especificação funcional para um novo contexto de implementação que não recebeu nem lê a fonte técnica. O novo contexto registra os documentos recebidos e não acessa o repositório de origem.
6. Se houver intenção de copiar ou adaptar código, interromper o fluxo de clean room e abrir revisão de licença, atribuição, obrigação de fonte e estratégia de distribuição.

## Regras para implementação do Klipper

- Cada história derivada de referência deve apontar para requisito próprio `UXR-*` ou spec do Klipper, nunca para arquivo da referência.
- Pull requests do Klipper devem conter somente código autoral, dependências declaradas ou código reutilizado com licença e avisos verificados.
- Nenhum trecho, texto de interface, asset, nome interno, schema ou estrutura criativa de referência entra por transcrição.
- Testes do Klipper descrevem o resultado que a pessoa usuária precisa obter, não reproduzem testes de uma referência.
- A proveniência é atualizada quando uma fonte muda de classe UX para técnica.

## Correção de escopo desta sessão

O PR de pesquisa contém documentação e não carrega código de referências. As observações de UX continuam utilizáveis como entrada de requisito. Contudo, por ter havido leitura limitada de configuração do Ghostfolio, este mesmo contexto não deve ser apresentado como uma equipe *clean* para uma futura implementação técnica inspirada no Ghostfolio. Uma implementação independente deve nascer de requisitos neutros em contexto separado; reuso literal segue a licença aplicável.
