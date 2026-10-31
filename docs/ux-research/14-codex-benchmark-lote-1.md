# Codex — Benchmark Lote 1: desfazer, exclusão e transferência

**Liberado por:** Roberto, 2026-10-31. Este documento libera somente as tarefas listadas abaixo da fila `docs/ux-research/13-tarefas-codex-por-app.md`. O restante da fila continua bloqueado.
**Repositório:** `Borussia80/Klipper`, a partir da `main` atual.
**Branch:** `codex/ux-benchmark-lote-1`. Somente documentação. Nenhum arquivo em `apps/` muda.
**Um PR por lote**, seguindo `CLAUDE.md`: uma demanda por vez, CI verde antes do merge.

---

## Por que este lote

O alfa D1–D3 do Klipper exige que o usuário exclua e restaure lançamentos e transferências sem quebrar saldo nem vínculo entre as pontas (`docs/alpha/01-operacao-segura.md`, item 3 da checagem de liberação). Na matriz `11-matriz-de-avaliacao.md`, essas são as jornadas com menos evidência:

- **Exclusão e recuperação:** 5 células N, 2 P.
- **Edição, cancelamento e desfazer:** 2 N, 5 P.
- **Transferência e contrapartida:** 1 N, 5 P. A criação está observada; a edição de uma ponta e o desfazer não.

Os requisitos de produto envolvidos são **UXR-03** (transferência atômica) e **UXR-04** (exclusão reversível), ambos P0. O portão de merge da própria pesquisa, ao final da matriz 11, exige ensaio deles.

O benchmark é cláusula pétrea do Klipper. A meta é trazer **comportamento observado e falhas encontradas**, não opinião sobre o que o app "provavelmente" faz.

---

## Leia antes de começar, nesta ordem

1. `docs/ux-research/09-observacao-ao-vivo.md`: ambientes, protocolo e dados sintéticos.
2. `docs/ux-research/11-matriz-de-avaliacao.md`: legenda O/P/N, UXR-03 e UXR-04, Ciclo A.
3. `docs/ux-research/12-protocolo-de-proveniencia-e-clean-room.md`: classe de cada fonte.
4. `docs/ux-research/13-tarefas-codex-por-app.md`: regras da fila e formato de relatório.
5. Os relatórios existentes em `docs/ux-research/relatorios/` de Actual, Cashew e Firefly (se houver), para **continuar** a numeração e não repetir o que já foi feito (A1, A2.1, A3.1, A3.2, C3.1, C3.2 já existem).

---

## Regras invioláveis

1. **Proveniência por classe de fonte.**
   - **Actual Budget (MIT): execução + código.** Antes de abrir qualquer arquivo, confirme o `LICENSE` no commit que vai ler e registre esse commit.
   - **Cashew (GPL-3.0) e Firefly III (AGPL-3.0): caixa-preta.** Só o produto rodando. Não abrir código, CSS, templates, migrations, configuração nem a documentação técnica interna.
2. **Nunca preencher de memória.** Se o ambiente não subir, o navegador não alcançar a porta ou a rede estiver bloqueada, registre `bloqueado: <motivo>` na linha e siga para a próxima tarefa. Não complete reação com conhecimento prévio do app, documentação ou "o que deveria acontecer".
3. **Regra em palavras próprias.** Nada de nomes de classes, funções, tabelas, colunas, trechos de código ou textos de interface copiados. Rótulos de botão podem ser citados entre crases apenas quando forem indispensáveis para descrever a ação.
4. **Dados sintéticos e descartáveis.** Sem login externo, sincronização, banco, corretora ou IA. Ações destrutivas só sobre dados do laboratório.
5. **Não tocar no Klipper.** Este lote não lê nem altera `apps/`. Nada observado aqui vira código nesta sessão.
6. **Um commit por app**, prefixo `docs(ux):`.

---

## Ambientes

| App | Ambiente preferido | Alternativa | Observação |
|---|---|---|---|
| Actual Budget | servidor oficial local, porta 4105 | demo pública oficial | A2 e A3 podem usar a demo; registre qual foi usado |
| Cashew | PWA oficial | — | Não iniciar login nem sincronização |
| Firefly III | imagem oficial local isolada, porta 4104 | demo pública oficial | A demo é compartilhada e reinicia; se reiniciar no meio de uma tarefa, refaça a tarefa inteira e anote |

Nenhum ambiente compartilha banco, cookie, volume ou porta com o Klipper.

---

## Instrumentação

Use **Playwright MCP** para conduzir o navegador, se estiver disponível nesta sessão. Para cada linha do relatório:

- **Captura de tela** do estado depois da ação, salva em `docs/ux-research/prints/<app>/lote-1-<ID>.png` e citada pelo `#` da linha.
- **Saldos lidos da tela**, nunca calculados por você: anote os valores exibidos de cada conta envolvida antes e depois.
- **axe-core** no estado final de cada tarefa, se disponível: registre só a contagem de violações por impacto (`critical`, `serious`, `moderate`, `minor`) e os tipos de regra. Isso é evidência auxiliar para UXR-12. **Não** altera a linha de acessibilidade da matriz, porque não é o ciclo C completo.

Se Playwright ou axe não estiverem disponíveis, conduza manualmente e registre `instrumentação: manual` no cabeçalho do relatório. Não invente contagem do axe.

---

## Dados sintéticos do lote

Crie em cada app, antes da primeira tarefa:

| Conta | Tipo | Saldo inicial |
|---|---|---|
| `Lab A` | corrente | R$ 1.000,00 |
| `Lab B` | poupança ou corrente | R$ 500,00 |

Categorias: `Mercado` (despesa) e `Renda` (receita). Se o app exigir orçamento para mostrar saldo de categoria, crie o limite `Mercado = R$ 300,00` no mês corrente.

Movimentos base em `Lab A`:

1. Receita `Lab salário` R$ 200,00 em `Renda`.
2. Despesa `Lab mercado 1` R$ 45,90 em `Mercado`.
3. Despesa `Lab mercado 2` R$ 12,34 em `Mercado`.

Anote os saldos exibidos depois da carga: é o **estado zero** de todas as tarefas.

---

## Tarefas

Cada tarefa é feita em **1440 px**. As marcadas com 📱 também em **390 px**, como linhas separadas (`F6.1` desktop, `F6.2` 390 px).

### Actual Budget — MIT · execução + código

**A2 · UXR-04 · Edição, cancelamento e desfazer (P)**

| Passo | Ação | Conferir na tela |
|---|---|---|
| A2.2 | Excluir `Lab mercado 2` | lista, saldo de `Lab A`, saldo da categoria `Mercado` |
| A2.3 | Desfazer a exclusão | os mesmos três valores voltaram ao estado anterior? |
| A2.4 | Editar o valor de `Lab mercado 1` para R$ 54,90 | os três valores |
| A2.5 | Desfazer a edição | voltou para R$ 45,90 e os saldos voltaram? |
| A2.6 | Fazer duas alterações seguidas (excluir `Lab mercado 2`, depois editar `Lab mercado 1`) e desfazer duas vezes | a ordem do desfazer, e se o segundo desfazer restaura a exclusão |
| A2.7 | Recarregar a página depois de A2.6 e tentar desfazer | o desfazer sobrevive à recarga? |

**Código (MIT):** descreva em palavras próprias o que é guardado para permitir desfazer, até onde ele volta e se sobrevive a recarga. Registre commit e arquivos consultados na coluna Fonte.

**A3 · UXR-03 · Transferência (continuação de A3.1 e A3.2)**

| Passo | Ação | Conferir na tela |
|---|---|---|
| A3.3 | Criar transferência R$ 100,00 de `Lab A` para `Lab B` | os dois saldos e se as duas pontas aparecem vinculadas |
| A3.4 | Editar o valor **só na ponta de destino** para R$ 120,00 | a ponta de origem acompanhou? os dois saldos? o vínculo continua? |
| A3.5 | Editar a data **só na ponta de origem** | a outra ponta acompanhou? |
| A3.6 | Excluir a transferência a partir da ponta de destino | as duas pontas saíram? os dois saldos voltaram? |
| A3.7 | Desfazer a exclusão | as duas pontas voltaram **vinculadas**, ou voltaram como movimentos soltos? |

**Código (MIT):** descreva a regra que mantém as duas pontas coerentes na edição e se a gravação é tudo-ou-nada.

### Cashew — GPL-3.0 · caixa-preta

**C3 · UXR-03 · Transferência (continuação de C3.1 e C3.2)**

| Passo | Ação | Conferir na tela |
|---|---|---|
| C3.3 | Criar transferência R$ 40,00 de `Lab A` para `Lab B` | os dois saldos |
| C3.4 📱 | Editar o valor só na ponta de destino para R$ 60,00 | a origem acompanhou? os dois saldos? |
| C3.5 | Excluir **só uma** das pontas, se o app oferecer a escolha | o que acontece com a ponta restante e com os saldos |
| C3.6 | Procurar forma de restaurar a exclusão | existe? onde? por quanto tempo? |

### Firefly III — AGPL-3.0 · caixa-preta

**F2 · UXR-03 · Transferência**

| Passo | Ação | Conferir na tela |
|---|---|---|
| F2.1 | Criar transferência R$ 100,00 de `Lab A` para `Lab B` | os dois saldos e a representação da contrapartida |
| F2.2 | Editar o valor para R$ 120,00 | as duas contas acompanharam? |
| F2.3 | Tentar editar uma ponta isoladamente, se o app permitir | o app impede, alerta ou aceita? |
| F2.4 | Excluir a transferência | os dois saldos voltaram? |

**F6 📱 · UXR-04 · Exclusão e recuperação**

| Passo | Ação | Conferir na tela |
|---|---|---|
| F6.1 | Excluir `Lab mercado 2` em 1440 px | confirmação exibida, saldo de `Lab A`, orçamento de `Mercado` |
| F6.2 | Procurar restauração (lixeira, histórico, desfazer) | existe? como se chega? o saldo volta? |
| F6.3 | Repetir F6.1 e F6.2 em 390 px com `Lab mercado 1` | a confirmação e a restauração são alcançáveis no mobile? |

---

## Formato do relatório

Acrescente as linhas ao relatório existente de cada app em `docs/ux-research/relatorios/<app>.md`. Crie `firefly-iii.md` se ainda não existir, com o cabeçalho da fila 13 e a linha extra:

```markdown
- Instrumentação: Playwright MCP + axe-core | manual
```

Uma tabela por tarefa, com as colunas da fila 13:

| # | Estado inicial | Ação | Reação na tela | Reação nos dados (saldo, lista, orçamento) | Fonte | Regra extraída | Teste de aceite no Klipper |
|---|---|---|---|---|---|---|---|

Exigências para cada linha:

- **Estado inicial** e **Reação nos dados** com os **saldos exibidos** de todas as contas envolvidas, antes e depois.
- **Fonte:** `execução`, `código · <arquivo>@<commit>` (só Actual) ou ambos. Linha só de código não marca O.
- **Teste de aceite no Klipper:** escrito para o Klipper, citando UXR-03 ou UXR-04, verificável por teste automatizado. Use `—` se a linha não gerar teste.
- **Falha observada:** quando o app perder vínculo, deixar saldo incoerente ou não oferecer recuperação, escreva `FALHA:` no início da coluna Regra extraída. Falhas das referências são o insumo mais valioso deste lote.

Ao fim de cada relatório, liste os testes de aceite novos ou alterados, agrupados por UXR.

---

## Fechamento de cada app (no mesmo commit)

1. Atualizar na matriz 11 somente as células daquele app nas linhas **Edição, cancelamento e desfazer**, **Transferência e contrapartida** e **Exclusão e recuperação**, com base apenas em linhas de execução. Linha `bloqueado` não muda célula.
2. Atualizar a coluna "Leitura responsável" dessas três linhas, se o resultado mudar a conclusão.
3. Acrescentar a sessão no `07-registro-pi.md`: fontes, commit lido (só Actual) e confirmação de que nenhum código foi copiado.
4. Se o Actual teve novo código lido, atualizar o commit no `12`.

---

## Entrega e parada

Ao terminar os três apps, abra **um** PR com:

- **Resumo:** células da matriz que mudaram (de → para), por app.
- **Falhas encontradas:** todas as linhas marcadas `FALHA:`, com o UXR afetado.
- **Testes de aceite propostos** para o Klipper, por UXR.
- **Bloqueios:** tarefas não executadas e motivo.

Depois do PR, **pare**. Não inicie outros lotes da fila 13, não proponha implementação no Klipper e não altere specs de domínio. A revisão e a decisão do que vira requisito são do Roberto.
