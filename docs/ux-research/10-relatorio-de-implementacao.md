# 10 — Relatório de implementação: padrões observados e decisões para o Klipper

**Status:** primeiro ciclo de observação ao vivo; insuficiente para encerrar decisões de produto — 2026-10-20
**Escopo:** categorias, entrada rápida, painel, contas e orçamento.
**Base factual:** `09-observacao-ao-vivo.md`. Este documento transforma evidência em proposta própria; não reproduz interface, código, assets ou textos das referências.

> Antes de implementar ou usar este relatório como justificativa de merge, consultar a [matriz de avaliação](11-matriz-de-avaliacao.md). Ela separa evidência completa, parcial e ausente, classifica gravidade e associa cada decisão a um critério de aceite.

## Síntese executiva

O Klipper deve concentrar sua próxima evolução em cinco capacidades conectadas: uma taxonomia simples de dois níveis, lançamento móvel com baixa fricção, correção confiável pós-importação, painel orientado a patrimônio e contas com leitura temporal. As referências convergem em quatro princípios úteis:

1. **Preparar configurações uma vez; lançar muitas vezes.** Moeda, taxonomia e contas não podem disputar atenção com valor, data e categoria durante um lançamento.
2. **O estado vazio tem uma única continuação principal.** Sem dados, orientar a primeira ação; com dados, priorizar leitura e alertas.
3. **Estruturas financeiras devem explicar sua consequência.** Categoria organiza, conta dá contexto de saldo, orçamento informa ritmo e alerta sempre oferece uma ação.
4. **Não calcular além da evidência disponível.** Uma fotografia de saldo sustenta patrimônio; rentabilidade, volatilidade e retorno exigem histórico de transações ou preços compatíveis.

## Decisões propostas

| Frente | Decisão para o Klipper | Evidência observada | Resultado esperado |
|---|---|---|---|
| Categorias | Limitar a categoria a pai + filha; criar, ordenar, ocultar e editar em Configurações | seleção opcional de taxonomia com grupos expansíveis no ezBookkeeping | escolha rápida e relatórios coerentes sem árvore profunda |
| Entrada mobile | Destacar “+” na navegação inferior; abrir folha de lançamento já focada no valor | Cashew mantém a transação como ação central, mesmo apresentando várias áreas; o fluxo observado hoje pede título/categoria antes do valor | lançamento em até quatro decisões após o valor |
| Movimentos importados | Abrir uma fila persistente de revisão com filtros salvos, edição em linha/lote e desfazer | a separação entre configurar e operar das referências reduz troca de contexto | importação corrigível sem perder linhas ou filtros |
| Painel | Começar com patrimônio, evolução temporal e alertas acionáveis; ocultar cards sem dados | Sure usa continuação única no estado vazio e deixa contas como base da leitura | painel compreensível em menos de uma olhada |
| Conta e orçamento | Tela de conta com saldo atual, histórico, próximos itens e orçamento por disponível/dia | fluxo de conta do Sure coleta saldo, data, moeda e subtipo; Cashew introduz orçamento como período e ritmo | saldo com contexto e orçamento que orienta a decisão de hoje |

## Complemento comparativo: Firefly III e Actual Budget

| Referência | Ponto mais útil | Limite a não transportar | Aplicação própria no Klipper |
|---|---|---|---|
| Firefly III | histórico de conta auditável: saldo acumulado, contrapartida, categoria, orçamento, transferências e divisões | grade muito larga e navegação desktop densa, sem reorganização adequada em 390 px | detalhe de conta com linha temporal e detalhe progressivo; não expor todas as colunas na lista mobile |
| Actual Budget | orçamento operacional: saldo por categoria, excesso consolidado e ação para cobrir; previsto, vencendo e atrasado no histórico | envelope completo adiciona um modelo mental e regras de alocação que o Klipper ainda não decidiu adotar | alertas de orçamento acionáveis, saldo por ritmo, lançamentos previstos no mesmo histórico e navegação inferior mobile |

## Complemento comparativo: Wealthfolio e Ghostfolio

| Referência | Ponto mais útil | Limite a não transportar | Aplicação própria no Klipper |
|---|---|---|---|
| Wealthfolio | separação explícita entre fotografia de posições e histórico transacional; histórico de saldos datados; métrica indisponível explicada em vez de zerada | onboarding longo e métricas de investimento antes de existir base suficiente | conta pode registrar saldo/manual datado e alimentar evolução; retorno e risco só aparecem quando o contrato de dados os sustentar |
| Ghostfolio | visão de patrimônio que inclui ativos, reserva e passivos, com composição por dimensões; primeira conta e total como estado funcional | dependência de cotação, benchmark e análises de mercado para entregar valor inicial; carregamento sem erro acionável quando uma dependência falha | modelar desde já ativo/passivo, grupo de conta, classe e liquidez; adiar mercado, benchmark e recomendações para uma fase orientada por necessidade real; sempre oferecer recuperação em falha de carregamento |

## Especificações funcionais de referência

### 1. Categorias em dois níveis e Configurações

**Modelo de dados e regra de uso**

- Uma categoria pode ser de receita ou despesa; transferência não usa categoria de gasto.
- Uma categoria de topo pode ter filhas; uma filha não pode ter descendentes.
- Categorias de topo não devem receber novo lançamento quando tiverem filhas ativas; a interface pede uma filha. Movimentos históricos continuam legíveis.
- Ocultar impede seleção futura sem quebrar histórico, filtros ou importações anteriores.

**Superfícies**

- Em Configurações, a pessoa vê uma árvore de dois níveis por tipo, com ações de criar filha, editar, reordenar e ocultar.
- No lançamento, o seletor oferece primeiro os grupos e depois as filhas, com busca por qualquer termo. Recentes podem aparecer antes, mas sem inventar uma terceira hierarquia.
- Na importação, uma linha sem categoria entra na fila de revisão; a atribuição pode ser aplicada a múltiplas linhas compatíveis.

**Aceite**

1. É impossível criar neta de categoria.
2. Uma categoria oculta permanece em movimentos anteriores, mas não aparece em novo lançamento.
3. A escolha `Alimentação > Mercado` pode ser feita por teclado e por toque sem abrir Configurações.

**Evidência adicional do ambiente executável:** a lista de categorias do ezBookkeeping separa tipos de movimento e apresenta a categoria primária como contexto explícito das filhas. Para o Klipper, a mesma clareza deve aparecer sem converter o seletor de lançamento em uma tela de administração.

### 2. Lançamento rápido mobile e navegação inferior

**Composição própria sugerida**

- Navegação inferior com quatro destinos (Início, Movimento, Orçamento e Mais) e a ação `+` ao centro.
- O `+` abre uma folha modal ancorada abaixo, não uma troca de rota. O primeiro foco é o valor; tipo de movimento (despesa, receita, transferência) fica visível e alternável. Esta é uma melhoria deliberada sobre o fluxo observado, que começa por título/categoria.
- Em seguida, conta e categoria são exigidas somente quando necessárias; data, descrição, recorrência e anexos entram em “mais opções”.
- Salvar e editar mostram confirmação curta com **Desfazer**. Cancelar descarta apenas o rascunho local, com confirmação somente se houver campos preenchidos. O Cashew confirmou o segundo comportamento; nesta rodada não exibiu desfazer após salvar/editar.

**Métrica inicial**

- Com conta e categoria recentes, registrar uma despesa deve exigir valor, confirmação de categoria/conta e salvar: no máximo quatro toques após tocar `+`.
- O teclado numérico não pode cobrir o botão de salvar nem esconder a categoria selecionada.
- Em 390 px, uma linha de movimento não pode depender de rolagem horizontal para revelar conta, valor ou sua ação de correção.

### 3. Busca, filtros e correção pós-importação em Movimento

**Fila de revisão**

- Ao concluir a importação, enviar para `Movimentos > Revisar importação`, com contador de pendências e deep link preservável.
- Separar de maneira explícita a origem/formato da importação, o mapeamento de colunas, a revisão e a conclusão. O mapeamento só aparece quando o formato exigir, evitando pedir configuração inexistente em exportações conhecidas.
- Filtros mínimos: período, conta, situação de importação, categoria ausente, possível duplicata e tipo. Eles devem permanecer na URL e sobreviver à edição.
- Mostrar a origem e o motivo de pendência em texto claro. Nunca transformar uma estimativa de duplicata em descarte automático.
- Permitir alteração de categoria, conta, data e descrição no contexto da lista; ações em lote devem ter resumo e desfazer.
- No mobile, representar cada linha como cartão compacto; filtros e seleção em lote devem abrir em folhas, e não em uma tabela comprimida.

**Aceite**

1. Filtrar “sem categoria” e corrigir dez linhas não perde a posição da lista.
2. Desfazer uma ação em lote restaura as linhas e o filtro.
3. Ao voltar de um detalhe, período e busca continuam iguais.

**Evidência adicional do ambiente executável:** ao aplicar busca no ezBookkeeping, período e termo foram serializados na URL. O Klipper deve adotar esse princípio para filtro, paginação e fila de revisão — com parâmetros próprios e legíveis — sem assumir que o usuário precise entender a URL.

### 4. Painel de patrimônio, evolução e alarmes

**Prioridade visual**

1. Patrimônio líquido atual e variação no período.
2. Evolução em gráfico temporal e distribuição por grupo de contas.
3. Alertas que pedem decisão, cada um com uma ação: revisar lançamento, pagar fatura, categorizar pendência ou atualizar saldo.
4. Resumo de orçamento por ritmo, não um mural de métricas.

**Estados**

- Sem conta: explicar em uma frase o que aparecerá e oferecer “Adicionar primeira conta”.
- Com conta sem histórico: exibir patrimônio e pedir movimentos ou uma atualização de saldo, sem renderizar gráfico fictício.
- Sem alertas: remover a seção ou mostrar estado compacto de tranquilidade; não reservar uma área grande vazia.

### 5. Detalhe de conta, histórico de saldo e orçamento diário

**Detalhe de conta**

- Cabeçalho com saldo, data da última atualização e ação contextual (novo movimento ou atualizar saldo).
- Linha temporal de saldos, não apenas soma de movimentos; destacar pontos de ajuste e importação.
- Separar saldo realizado de saldo previsto se houver itens agendados. A data de abertura estabelece o primeiro ponto conhecido.

**Evidência adicional do ambiente executável:** o fluxo do Sure solicita saldo inicial e data de abertura, mas a criação da conta sintética não foi concluída nesta sessão: após preencher e enviar, o formulário permaneceu aberto sem sucesso ou erro visível. O princípio para o Klipper continua válido, porém precisa ser validado no próprio produto com dados sintéticos: histórico de saldo não pode ser inferido apenas da fotografia atual.

**Evidência adicional do Wealthfolio local:** uma conta configurada como fotografia registrou um saldo de caixa datado e passou a exibir patrimônio, valores de caixa/investimento/contábil e histórico de snapshots. Em contrapartida, retorno, P&L, volatilidade e drawdown ficaram indisponíveis com uma explicação de pré-requisito. O Klipper deve seguir a mesma honestidade sem herdar a interface: histórico de saldo é válido, mas não é histórico de performance.

**Evidência adicional do Ghostfolio local:** uma conta inicial e a linha de total tornam a página de contas funcional mesmo antes de haver atividades. O Klipper pode usar esse princípio como orientação inicial, desde que a conta de exemplo não seja confundida com dado real e possa ser editada ou removida. Também fica explícito um requisito transversal: `loading` precisa expirar em erro compreensível, com tentar novamente e diagnóstico técnico fora da superfície principal.

Quando uma conta usar histórico transacional, o formulário do Wealthfolio primeiro pede a natureza da atividade e só então mostra campos específicos, mantendo a conta de origem já contextualizada. Para o Klipper, aplicar esse princípio como redução de erro: movimento comum mantém o caminho curto; operações patrimoniais específicas revelam campos apenas depois do tipo, sem misturar um aporte, uma transferência e uma compra de ativo.

**Ritmo de orçamento**

- Para cada orçamento ativo, calcular: disponível, dias restantes, limite diário e comparação com o ritmo esperado até hoje.
- Usar linguagem clara: “R$ X por dia até o fim do ciclo” e “acima/abaixo do ritmo”, acompanhada de cor e ícone — nunca cor isolada.
- Não indicar falha enquanto o período estiver dentro do ritmo, mesmo que já tenha consumido grande parte do limite cedo em um ciclo curto.

**Evidência adicional do ambiente executável:** o Cashew apresentou, em um orçamento local de R$ 200 com R$ 50 já consumidos, saldo restante, fração do período e uma recomendação de gasto por dia. O Klipper deve adotar o cálculo de ritmo, com apresentação e redação próprias.

## Ordem recomendada de entrega

1. **Fundação:** modelo de categorias, tela de Configurações e seletor reutilizável.
2. **Operação:** lançamento mobile, nova navegação inferior e confirmação com desfazer.
3. **Confiabilidade:** filtros persistentes e fila de revisão de importação.
4. **Leitura:** detalhe de conta, histórico de saldo e painel de patrimônio.
5. **Orientação:** orçamento por ritmo e alertas acionáveis.
6. **Patrimônio estruturado:** ativos/passivos, grupos de conta e fotografia de saldo antes de indicadores de investimento.

Essa ordem reduz retrabalho: lançamento, importação e orçamento compartilham o mesmo contrato de categoria, conta e data.

## Restrições de design

- Aplicar os tokens e a direção náutica existentes do Klipper; preservar Inter, Space Grotesk e Phosphor.
- Não importar a aparência Material, ilustrações, cópia textual, cores, medidas, componentes ou assets das referências.
- Implementar comportamento responsivo, e não uma versão desktop encolhida: navegação e formulário podem mudar de apresentação; regras e dados permanecem consistentes.

## Lacunas a fechar no próximo ciclo

- Medir o desfazer após exclusão de um lançamento sintético em mobile (depende de confirmação pontual para descarte local).
- Validar busca/filtro, importação e edição em lote com o conjunto sintético completo.
- Confirmar quais alertas são suficientemente frequentes e acionáveis para merecer o painel inicial.
- Testar, com conta sintética local, como uma conta transacional recupera erro de dado incompleto e como sua atividade altera o painel de patrimônio.
- Testar as propostas com o Klipper em 390 px e 1440 px antes de iniciar uma implementação ampla.
- Executar os ciclos A, B e C da matriz de avaliação, com registro de evidência e atualização da cobertura antes de declarar o estudo encerrado.
