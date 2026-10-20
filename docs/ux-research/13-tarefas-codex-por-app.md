# 13 — Tarefas do Codex: estudo por app (ação → reação)

**Status:** fila de trabalho — criada em 2026-10-20, **não iniciar antes de ser liberada pelo Roberto**.
**Branch:** `codex/ux-live-research` (só documentação; nenhum código do Klipper muda nesta fila).
**Objetivo:** fechar as células `N`/`P` da [matriz 11](11-matriz-de-avaliacao.md) e dar evidência aos requisitos
UXR-01, 03, 04, 06, 07, 09 e 11, com relatórios que registram cada ação executada e a reação obtida.

## Leia antes de começar, nesta ordem

1. [09 — Observação ao vivo](09-observacao-ao-vivo.md): ambientes, protocolo e dados sintéticos padrão.
2. [11 — Matriz de avaliação](11-matriz-de-avaliacao.md): legenda O/P/N, requisitos UXR e ciclos A/B/C.
3. [12 — Protocolo de proveniência](12-protocolo-de-proveniencia-e-clean-room.md): classes de fonte e o que pode
   ou não ir para um relatório.
4. Este documento.

## Regras desta fila

1. **Leitura de código só nos apps MIT** (ezBookkeeping e Actual Budget). Antes de abrir qualquer arquivo,
   confirme o `LICENSE` no commit que vai ler e anote o commit. Se a licença não for MIT, pare e trate o app
   como caixa-preta.
2. **Apps copyleft são caixa-preta** (Sure, Cashew, Firefly III, Wealthfolio, Ghostfolio): só o produto rodando.
   Não abra código, CSS, templates, migrations nem configuração. No Ghostfolio, nenhuma leitura além da que o
   [07](07-registro-pi.md) já registra.
3. **Nunca preencher de memória.** Se o ambiente não subir, o navegador não alcançar a porta ou o sandbox
   bloquear a rede, registre `bloqueado: <motivo>` na linha e siga para a próxima tarefa. Não complete a reação
   com o que você sabe do app, com a documentação ou com o que "deveria" acontecer.
4. **Regra em palavras próprias.** A coluna "Regra extraída" descreve o comportamento. Não leva nomes de
   classes, funções, tabelas, colunas, trechos de código nem textos de interface copiados.
5. **Dados sintéticos e descartáveis**, conforme o 09. Não conectar banco, corretora, sincronização, login
   externo nem IA. Ações destrutivas (excluir, desfazer) são permitidas **só** sobre dados sintéticos do
   laboratório; esta lista vale como a confirmação pontual pedida no 09 para o Cashew.
6. **Um commit por app**, prefixo `docs(ux):`, conforme terminar. Não acumule trabalho fora de commit.
7. **Larguras:** cada tarefa marcada com 📱 é feita em 1440 px e 390 px.

## Formato do relatório

Um arquivo por app em `docs/ux-research/relatorios/<app>.md`, com este cabeçalho:

```markdown
# <App> — relatório ação → reação
- Licença / classe (12): …
- Versão ou commit: …
- Ambiente: … (porta, imagem, demo)
- Data: …
- Tarefas executadas / bloqueadas: …
```

E uma tabela por tarefa:

| # | Estado inicial | Ação | Reação na tela | Reação nos dados (saldo, lista, orçamento) | Fonte | Regra extraída | Teste de aceite no Klipper |
|---|---|---|---|---|---|---|---|
| E1.3 | 2 contas, 1 movimento importado | Reimportar o mesmo arquivo | … | … | execução · `<arquivo>@<commit>` | … | UXR-06: … |

- **Fonte** diz se a linha veio de `execução`, de `código` (arquivo e commit, só MIT) ou de ambos. Linha só de
  código não basta para marcar `O` na matriz: a reação precisa ser vista rodando.
- **Teste de aceite** é escrito para o Klipper, citando o UXR. Se a linha não gerar teste, deixe `—`.
- Capturas vão em `docs/ux-research/prints/<app>/`, citadas pelo `#` da linha.

## Lote 0 — piloto (fazer primeiro e parar)

Importação com deduplicação no **ezBookkeeping (E1)** e no **Actual Budget (A1)**, com execução e código.
Ao terminar, pare e entregue os dois relatórios para revisão. Os demais lotes só começam depois que o nível de
detalhe for aprovado.

Arquivo sintético único para os dois (CSV, gerado por você e salvo em `docs/ux-research/prints/dados/`):
10 linhas novas, 2 duplicatas exatas, 1 quase duplicata (mesmo valor e data, descrição diferente), 1 linha sem
categoria, 1 valor inválido, 1 transferência entre contas próprias.

---

## ezBookkeeping — MIT · código + execução · porta 4101

| ID | UXR / matriz | Tarefa |
|---|---|---|
| **E1** | UXR-06 · Importação (P) | **Piloto.** Importar o CSV sintético. O bloqueio anterior foi o seletor de arquivo oculto: use upload por automação de navegador (definir arquivo no input) ou pela API do próprio app. Registrar cada etapa: escolha de formato, mapeamento, revisão, conclusão. Reimportar o mesmo arquivo. No código, localizar o critério de duplicata e descrevê-lo em palavras próprias: quais campos comparam, tolerância, o que acontece com a quase duplicata. |
| E2 | UXR-06, UXR-04 · Importação (P) | Após importar, corrigir categoria em lote em 10 linhas; tentar desfazer o lote. Registrar se existe desfazer e o que o código guarda para isso. |
| E3 | UXR-03 · Ciclo A2 | Criar transferência entre duas contas; editar o valor de uma ponta; excluir. Conferir os dois saldos após cada passo. No código, descrever como as duas pontas ficam ligadas e se a gravação é tudo-ou-nada. |
| E4 | UXR-04 · Edição/desfazer (P) | Excluir um movimento comum. Registrar confirmação, efeito no saldo e se há forma de restaurar. |
| E5 | UXR-01 · Erro (P) | Com um formulário de movimento preenchido, parar o container e salvar. Registrar mensagem, tempo até aparecer, se o rascunho sobrevive e o que acontece ao religar. |
| E6 📱 | UXR-05, UXR-08 | Filtrar por conta e período, abrir um movimento, editar e voltar. Registrar se filtro, posição e URL se mantêm. |

## Actual Budget — MIT · código + execução · demo oficial ou servidor local

Preferir servidor local oficial (porta 4105) para as tarefas de erro; a demo pública serve para as demais.
Repositório: `github.com/actualbudget/actual`.

| ID | UXR / matriz | Tarefa |
|---|---|---|
| **A1** | UXR-06 · Importação (P) | **Piloto.** Importar o mesmo CSV sintético numa conta. Reimportar. Registrar como o app trata duplicata e quase duplicata, e se pede confirmação. No código, descrever o critério de correspondência em palavras próprias. |
| A2 | UXR-04 · Edição/desfazer (P) | Excluir um movimento e desfazer; editar um valor e desfazer; desfazer duas vezes seguidas. Conferir lista, saldo da conta e saldo da categoria após cada passo. No código, descrever o que é guardado para desfazer e até onde ele volta. |
| A3 | UXR-03 · Ciclo A2 | Criar transferência entre duas contas; editar uma ponta; excluir; desfazer a exclusão. Conferir os dois saldos e o vínculo. No código, descrever a regra que mantém as pontas coerentes. |
| A4 | Criar conta (N) | Criar conta nova com saldo inicial e data. Registrar como o saldo inicial aparece no histórico. |
| A5 | UXR-09 · Orçamento (O) | Montar uma categoria dentro, uma acima e uma estourada. Registrar texto, cor, ícone e ação oferecida em cada uma. O modelo de envelopes **não** foi adotado: descreva a regra de estouro, não proponha adotar envelopes. |
| A6 | Conciliação (O) | Conciliar a conta com um saldo divergente. Registrar o que o app pede, o ajuste que cria e como o histórico mostra. |
| A7 | UXR-01 · Erro (P) | No servidor local, derrubar o servidor durante uma edição. Registrar mensagem, perda ou preservação do dado e ressincronização. |

## Sure — AGPL-3.0 · caixa-preta · porta 4100

| ID | UXR / matriz | Tarefa |
|---|---|---|
| S1 | UXR-01 · Criar conta (P) | Reproduzir a falha da criação de conta manual. Registrar status de rede e console do navegador (não o código). Tentar outro tipo/subtipo. Se continuar falhando, registrar e marcar S2–S5 como `bloqueado`. |
| S2 📱 | Conta preenchida (N) · Painel (O) | Com conta criada: painel preenchido, detalhe da conta, histórico de saldo e alertas. |
| S3 | UXR-04 · Edição/desfazer (N) | Editar, cancelar edição e excluir um movimento. Registrar confirmação e se há desfazer. |
| S4 | UXR-03 | Transferência entre duas contas: criar, editar, excluir; conferir os dois saldos. |
| S5 | UXR-06 · Importação (P) | Importar o CSV sintético até o fim; reimportar. |

Não habilitar nem configurar a área de IA.

## Cashew — GPL-3.0 · caixa-preta · PWA oficial

| ID | UXR / matriz | Tarefa |
|---|---|---|
| C1 | Criar conta (N) | Criar conta com saldo inicial. Registrar onde o saldo inicial aparece. |
| C2 | UXR-04 · Edição/desfazer (P) | Excluir um lançamento sintético e procurar forma de desfazer. Registrar efeito no saldo e no orçamento. |
| C3 | UXR-03 | Transferência entre duas contas: criar, editar, excluir; conferir os dois saldos. |
| C4 📱 | UXR-07 | Lançar despesa com conta e categoria recentes. Contar toques desde a ação de adicionar até salvar. Repetir três vezes e registrar o menor e o maior. |
| C5 | UXR-09 · Orçamento (O) | Orçamento com categoria dentro, acima e estourada. Registrar texto, cor, ícone e ação em cada estado. |

Não iniciar login nem sincronização.

## Firefly III — AGPL-3.0 · caixa-preta · demo pública ou container oficial local

A demo pública é compartilhada e reinicia. Para F5, subir a imagem oficial local isolada (porta 4104).

| ID | UXR / matriz | Tarefa |
|---|---|---|
| F1 | Criar conta (N) | Criar conta com saldo de abertura e data. Registrar como aparece no histórico. |
| F2 | UXR-03 · Ciclo A2 | Transferência: criar, editar uma ponta, excluir. Conferir os dois saldos. |
| F3 | Ciclo A3 | Criar movimento dividido em duas categorias; editar uma parte; excluir. Conferir categorias e orçamento. |
| F4 | Conciliação (P) | Conciliar uma conta com saldo divergente. Registrar o ajuste criado. |
| F5 | UXR-01 · Erro (N) | No container local: enviar formulário inválido e, depois, parar o banco e salvar. Registrar mensagem e preservação do formulário. |
| F6 📱 | UXR-04 · Edição/desfazer (P) | Excluir um movimento e procurar restauração. |

## Wealthfolio — AGPL-3.0 · caixa-preta · binário oficial, porta 4102

| ID | UXR / matriz | Tarefa |
|---|---|---|
| W1 | UXR-02 · lacuna do 10 | Em conta transacional: aporte, compra, venda e dividendo sintéticos (ativo fictício ou preço manual, sem provedor de mercado). Registrar como o painel de patrimônio muda após cada um e quando as métricas passam de "não calculável" a calculadas. |
| W2 | UXR-01 · lacuna do 10 | Atividade com dado incompleto (sem preço, sem data, quantidade zero). Registrar validação e recuperação. |
| W3 | UXR-04 · Edição/desfazer (N) | Editar e excluir uma atividade; registrar confirmação e efeito no histórico. |
| W4 📱 | Mobile (N) | Painel, conta e formulário de atividade em 390 px. |
| W5 | UXR-06 · Importação (P) | Importar CSV sintético de atividades com uma duplicata. |

## Ghostfolio — AGPL-3.0 · caixa-preta, contexto já marcado como dirty limitado · imagem oficial, porta 4103

| ID | UXR / matriz | Tarefa |
|---|---|---|
| G1 | UXR-04 · Edição/desfazer (N) | Criar, editar e excluir atividade. Registrar confirmação e efeito em contas e total. |
| G2 | UXR-11 | Sair, recuperar acesso com o token, tentar token inválido. Registrar mensagem, foco e ação oferecida em cada estado. |
| G3 📱 | Mobile (N) | Contas, atividades e painel em 390 px. |
| G4 | UXR-01 · Erro (P) | Enviar atividade inválida; registrar validação. Não repetir o teste de Redis já registrado. |

---

## Fechamento de cada app

Ao terminar um app, no mesmo commit:

1. Atualizar as células daquele app na [matriz 11](11-matriz-de-avaliacao.md), só com base em linhas de
   execução do relatório. Linha `bloqueado` não muda célula.
2. Acrescentar a sessão no [07](07-registro-pi.md): fontes, commit lido (MIT) e confirmação de que nenhum
   código foi copiado para o Klipper.
3. Se um app MIT teve código lido, atualizar a classe dele no [12](12-protocolo-de-proveniencia-e-clean-room.md).
4. Listar, no fim do relatório, os testes de aceite novos ou alterados por UXR.
