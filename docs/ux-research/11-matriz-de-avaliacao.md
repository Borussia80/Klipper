# 11 — Matriz de avaliação de jornadas e confiabilidade

**Status:** revisão de aprofundamento — 2026-10-20  
**Base factual:** `09-observacao-ao-vivo.md`.  
**Objetivo:** separar evidência observada, lacuna de pesquisa e requisito verificável antes de usar este estudo como base de implementação ou de merge.

**Proveniência:** a classificação UX/técnica de cada referência e a regra de separação de contexto estão em `12-protocolo-de-proveniencia-e-clean-room.md`.

## Como ler a matriz

- **O** — observado de ponta a ponta com estado relevante (vazio, preenchido, erro ou sucesso).
- **P** — observado parcialmente; não autoriza concluir comportamento não visto.
- **N** — não observado; continua como hipótese ou lacuna.
- **Risco**: P0 bloqueia integridade/recuperação de dado financeiro; P1 compromete jornada principal; P2 gera atrito ou leitura equivocada; P3 é melhoria de acabamento.

Uma referência não é uma especificação. A matriz registra comportamentos de produtos distintos para formular e testar regras próprias do Klipper.

## Cobertura comparativa por jornada

| Jornada / estado exigido | Sure | ezBookkeeping | Cashew | Firefly III | Actual Budget | Wealthfolio | Ghostfolio | Leitura responsável |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Primeiro acesso, autenticação e retorno à sessão | P | O | O | P | P | O | O | Há boas referências de onboarding; recuperação e expiração ainda precisam de roteiro próprio no Klipper. |
| Criar conta e saldo inicial | O | O | N | N | N | O | O | No Sure, a criação manual local concluiu com confirmação e histórico. Cashew, Firefly e Actual continuam sem criação de conta registrada no 09. |
| Conta preenchida, evolução e histórico | O | P | P | O | O | O | P | Sure mostrou saldo, variação, gráfico, atividade, cartão e financiamento; a conferência mobile desses detalhes continua pendente. |
| Lançamento de despesa/receita rápido | O | O | O | P | O | P | P | Sure validou o campo obrigatório e atualizou detalhe e atividade; Cashew continua a referência mobile principal. |
| Edição, cancelamento e desfazer | P | P | P | P | P | N | N | Sure persistiu edição automática, mas não mostrou cancelar ou desfazer; desfazer após salvar/excluir segue não confirmado. |
| Transferência e contrapartida | P | P | N | O | P | P | N | Sure criou as duas pontas, mas remover o vínculo preservou movimentos órfãos; o fluxo ainda não é referência para integridade. |
| Exclusão e recuperação | P | N | P | N | N | N | N | Sure confirmou remoção do vínculo, porém sem restauração e mantendo transações; não concluir padrão de exclusão. |
| Busca, filtros e persistência de contexto | O | O | O | P | O | N | N | Há evidência para filtros persistentes; filtros patrimoniais ainda precisam de estudo. |
| Importação, deduplicação e correção em lote | P | O | N | N | O | P | N | Sure chegou à limpeza e exibiu erro por linha para datas futuras, mas não confirmou importação/reimportação. ezBookkeeping inseriu duplicatas de conteúdo; Actual bloqueou exatas e quase duplicata. |
| Conciliação e saldo previsto | N | N | N | P | O | N | N | Actual oferece melhor evidência; a regra precisa ser validada por cenários sintéticos do Klipper. |
| Orçamento, ritmo e excedente | P | N | O | O | O | N | N | Ritmo diário, período e alerta acionável têm evidência; não há decisão de adotar envelopes. |
| Painel, alertas e estado vazio | O | P | O | P | O | O | P | Existe base para hierarquia, mas alertas do Sure preenchido continuam sem evidência. |
| Erro, validação e recuperação | O | P | P | N | P | P | P | Sure bloqueou descrição ausente e enumerou o erro de data por linha; ainda falta ensaio sistemático de rede, permissão, duplicata e conflito. |
| Mobile a 390 px, densidade e navegação | P | P | O | O | O | N | N | Cashew e Actual sustentam a proposta mobile; patrimônio/investimentos ainda devem passar pelo mesmo ensaio. |
| Acessibilidade por teclado, foco, leitor de tela e contraste | N | N | N | N | N | N | N | Nenhuma conclusão; é exigência de validação do Klipper, não uma comparação encerrada. |

## Achados priorizados → requisitos do Klipper

| ID | Evidência e problema | Gravidade | Decisão / requisito verificável | Critério de aceite |
|---|---|---|---|---|
| UXR-01 | Uma falha anterior de conta no Sure não se repetiu: a execução atual confirmou criação, detalhe e histórico. Ghostfolio sem Redis mostrou carregamento contínuo. | P0 | Toda mutação deve terminar em sucesso confirmado, erro recuperável ou estado pendente com prazo; nunca pode ficar silenciosa ou indefinida. | Simular erro de API e indisponibilidade: em até 10 s, mostrar mensagem clara, preservar dados digitados e oferecer `Tentar novamente`. |
| UXR-02 | Saldo manual e histórico transacional permitem leituras diferentes; no Sure, compra elevou a dívida do cartão e pagamento a reduziu por transferência, mas a tela de extratos só mostrou cobertura/zero arquivos, sem ciclo, fechamento ou vencimento. Em financiamento, o cronograma separou principal e juros, mas uma transferência de parcela não alterou o principal registrado. Wealthfolio torna métricas indisponíveis quando falta base. | P0 | Separar `saldo/fotografia`, `movimento`, `dívida` e `performance` no domínio e na interface. Cartão precisa de fatura, ciclo e vencimento explícitos; financiamento precisa de alocação explícita entre principal e juros. | Compra no cartão aumenta dívida e categoria sem saída de caixa; pagamento baixa a fatura identificada e atualiza caixa, saldo devedor e vencimento sem recarga manual. Parcela de financiamento mostra juros, principal e saldo posterior coerentes. |
| UXR-03 | Sure criou duas pontas e saldos coerentes, mas ao remover o vínculo preservou movimentos sem contrapartida. Também aceitou parcela de financiamento como transferência sem amortizar o principal registrado. Firefly segue como evidência complementar. | P0 | Transferência cria duas pontas vinculadas; edição e exclusão preservam ou restauram ambas atomicamente. Pagamento de dívida deve vincular também a alocação e a atualização de saldo. | Criar, editar, falhar e desfazer transferência: os dois saldos e o vínculo permanecem consistentes. Pagar dívida atualiza caixa, alocação e saldo devedor no mesmo resultado confirmado. |
| UXR-04 | Sure não mostrou desfazer e a remoção do vínculo não restaurou estado anterior; ações irreversíveis seguem lacuna crítica. | P0 | Exclusão financeira deve ser reversível por período definido ou exigir confirmação que explique o efeito no saldo e histórico. | Excluir movimento e desfazer: lista, saldo, orçamento e alertas retornam ao estado anterior. |
| UXR-05 | ezBookkeeping preserva busca/período; Cashew preserva filtros como chips. | P1 | Filtros, ordenação, paginação e fila de importação devem sobreviver a edição, retorno e URL/deep link quando aplicável. | Filtrar `sem categoria`, editar dez linhas e voltar: mesma consulta, seleção e posição continuam disponíveis. |
| UXR-06 | Sure mostrou erro por linha para datas fora do intervalo e edição in-line sem atualização perceptível; ezBookkeeping e Actual completaram seus pilotos com regras de duplicata diferentes. | P0 | Linhas importadas precisam de origem, estado, motivo de pendência e correção em lote reversível; duplicata nunca é descartada automaticamente. | Importar arquivo sintético com duplicata e linha incompleta: ambas ficam revisáveis e a ação em lote pode ser desfeita. |
| UXR-07 | Cashew bloqueia valor zero e confirma descarte; sua sequência não é necessariamente a mais curta. | P1 | Lançamento mobile abre no valor; valida somente o necessário por tipo e confirma descarte apenas se o rascunho mudou. | Em 390 px, registrar despesa recente em no máximo quatro toques depois de `+`; saída sem alteração não pergunta; saída alterada pergunta. |
| UXR-08 | Firefly é auditável, mas comprime tabela; Actual e Cashew reorganizam melhor em 390 px. | P1 | Nenhuma informação crítica de movimento depende de tabela horizontal no mobile. | Em 390 px, lista mostra tipo/categoria, valor, conta e data sem rolagem lateral; detalhe expõe contrapartida e saldo acumulado. |
| UXR-09 | Actual consolida estouro e dá ação; Cashew mostra ritmo diário. | P1 | Orçamento exibe disponível, dias restantes, ritmo diário e alerta com próxima ação, distinguindo planejado, previsto e realizado. | Cenários dentro/acima/estourado mudam texto, ícone e CTA de forma coerente; cor nunca é o único sinal. |
| UXR-10 | Estado vazio do Sure, Wealthfolio e Ghostfolio oferece uma continuidade clara; porém uma conta de exemplo pode ser confundida com dado real. | P2 | Estado vazio tem uma ação primária e explica o resultado; dados de demonstração, se existirem, devem ser identificados e removíveis. | Sem contas, há somente `Adicionar primeira conta` como CTA principal; sem histórico, não há gráfico fictício. |
| UXR-11 | Ghostfolio exige guardar token de recuperação; é uma proteção real, mas uma barreira se não houver explicação e confirmação. | P1 | Autenticação e recuperação devem ter contrato explícito: credencial, caminho de recuperação, sessão e comunicação de perda. | Criar conta, sair, recuperar acesso e tentar token inválido: cada estado tem mensagem específica, foco correto e ação segura. |
| UXR-12 | Acesso, validação e estados foram examinados visualmente; não houve ensaio formal de acessibilidade. | P1 | Toda jornada crítica deve ser navegável por teclado, com foco previsível, rótulos, erro associado ao campo e contraste conforme tokens. | Teste de teclado e leitor de tela em login, lançamento, transferência, filtro e confirmação de exclusão passa sem bloqueio. |

## Roteiro de aprofundamento obrigatório antes de fechar o estudo

### Ciclo A — integridade financeira

1. Criar conta, saldo inicial e três movimentos; conferir saldo após cada etapa.
2. Criar transferência entre duas contas, editar uma ponta, induzir falha e desfazer.
3. Criar movimento dividido e excluir/restaurar; conferir categorias, orçamento e histórico.
4. Registrar ajuste de saldo datado e verificar a linha temporal.

### Ciclo B — operação e recuperação

1. Aplicar busca/filtros, editar em linha e retornar ao mesmo contexto.
2. Importar arquivo sintético com duplicata, categoria ausente e valor inválido; revisar uma linha e dez linhas; desfazer.
3. Simular rede lenta, indisponibilidade e erro de validação; medir mensagem, persistência de rascunho e recuperação.
4. Criar, editar, cancelar e excluir lançamento no mobile; contar toques e confirmar que não há perda silenciosa.

### Ciclo C — leitura e acesso

1. Comparar 1440 px e 390 px para painel, conta, movimento, orçamento e alerta.
2. Auditar foco, rótulos, contraste e mensagens de erro nas cinco jornadas críticas.
3. Validar terminologia: `movimento`, `transferência`, `saldo disponível`, `saldo previsto`, `orçamento` e `patrimônio` mantêm o mesmo significado em toda a aplicação.

## Portão para merge e implementação

O PR de pesquisa **não deve ser tratado como estudo fechado** enquanto os requisitos UXR-03, UXR-04, UXR-06 e UXR-12 estiverem sem ensaio. Ele pode ser mergeado somente como documentação de descoberta, com as lacunas preservadas; não como autorização para implementar ou declarar prontas as jornadas financeiras.

Para iniciar implementação, cada história deve referenciar pelo menos um requisito UXR e trazer teste de aceitação correspondente. Para encerrar a pesquisa, atualizar esta matriz com data, ambiente, evidência e resultado de cada ciclo.
