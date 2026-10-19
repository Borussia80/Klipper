# 09 — Observação ao vivo: referências de UX/UI

**Início da sessão:** 2026-10-19
**Método:** instâncias isoladas, dados sintéticos, observação via navegador.
**Regra de sala limpa:** Sure (AGPL-3.0) e Cashew (GPL-3.0) são observados somente como produtos em execução. Nenhum código, CSS, template ou asset desses projetos é consultado ou reutilizado no Klipper.

## Ambientes de pesquisa

| Produto | Ambiente | Papel na pesquisa | Estado |
|---|---|---|---|
| Sure | container oficial local, porta 4100 | hierarquia desktop, patrimônio, contas e alertas | ativo |
| ezBookkeeping | container oficial local, porta 4101 | estrutura de categorias, filtros, importação e configurações | ativo |
| Cashew | PWA oficial | rapidez de lançamento e padrões mobile | ativo |

Os ambientes não compartilham banco, cookie, volume ou porta com o Klipper. As contas e transações criadas durante o estudo devem ser descartáveis e sintéticas.

## Protocolo de observação

Cada fluxo é registrado nas larguras **1440 px** e **390 px**, com quatro estados: vazio, preenchido, erro/validação e sucesso/desfazer. Para cada ação, registrar:

1. objetivo e ponto de entrada;
2. passos, decisões e atalhos necessários;
3. hierarquia visual, feedback, persistência de filtros e recuperação;
4. o que adaptar, descartar ou manter no Klipper;
5. critério de aceite verificável para a implementação própria.

## Dados sintéticos padrão

| Entidade | Cenário |
|---|---|
| Contas | conta corrente, cartão de crédito e poupança/investimento |
| Movimentos | renda, gasto recorrente, compra parcelada, gasto sem categoria e transferência |
| Categorias | Alimentação > Mercado; Moradia > Energia; Transporte > Combustível |
| Orçamento | uma categoria dentro do ritmo, uma acima do ritmo e uma estourada |
| Alertas | fatura próxima do vencimento, saldo previsto negativo e conta desatualizada |
| Importação | linhas novas, duplicata, linha sem categoria e linha corrigida em lote |

## Evidências iniciais

### Sure — entrada desktop

- A instância local encaminha o primeiro acesso diretamente ao cadastro, deixando claro que a instalação não tem usuário.
- A tela expõe o caminho alternativo de login, campos mínimos e regras explícitas de senha antes da ação.
- A mensagem contextualiza o passo seguinte de configuração depois da criação da conta.

**Hipótese para o Klipper:** o feedback de pré-requisito deve ser local e imediato em autenticação, nunca uma tentativa silenciosa de envio. Isso complementa o ajuste recente de sessão explícita após cadastro.

### Sure — onboarding, painel e inclusão de conta

- O onboarding é sequencial e curto: identidade, preferência regional/monetária e objetivos de uso. Cada etapa tem uma pergunta própria; idioma, moeda e formato de data mostram uma prévia antes de a pessoa seguir.
- A escolha de objetivos permite iniciar com um recorte de interesse (contas, fluxo, orçamento, investimentos), sem transformar a decisão em bloqueio posterior.
- O painel vazio mantém uma barra lateral de contas com os recortes **Todas / Ativos / Dívidas** e um único CTA de continuação para adicionar uma conta. A área principal não tenta simular gráficos sem informação.
- A inclusão começa pela natureza do ativo (dinheiro, investimento, cripto, propriedade, veículo ou outro) e, em seguida, separa **informar manualmente** de conectar uma instituição. O formulário manual pede nome, saldo, data de abertura, moeda e subtipo; detalhes avançados ficam recolhidos.
- O painel também exibe uma área opcional de IA. Ela foi deliberadamente ignorada nesta pesquisa: não foi habilitada, configurada nem recebeu dados.

**Hipótese para o Klipper:** em vez de uma tela genérica de “nova conta”, usar uma decisão inicial de natureza da conta e deixar integrações fora do caminho manual. No painel, mostrar patrimônio somente quando houver base de dados; no vazio, oferecer a próxima ação inequívoca.

### ezBookkeeping — entrada desktop

- Login apresenta credenciais, recuperação de senha, criação de conta e seletor de idioma na mesma superfície.
- O CTA começa indisponível antes de campos mínimos, reduzindo tentativa vazia.
- Existe uma entrada explícita para o modo móvel, útil como referência para diferenças reais de interação — não para duplicar as rotas do Klipper.

**Hipótese para o Klipper:** o CTA de autenticação deve expressar prontidão e os fluxos de recuperação precisam manter a pessoa fora da sessão até autenticação explícita.

### ezBookkeeping — categorias como decisão de configuração

- O cadastro é dividido em duas etapas visíveis. Depois de dados básicos e preferências locais, a segunda etapa pergunta se a pessoa quer usar categorias predefinidas.
- A taxonomia é apresentada antes da conclusão, organizada por natureza de movimento: receita, despesa e transferência. Cada grupo já traz categorias de topo expansíveis, sinalizando subcategorias sem abrir uma árvore infinita.
- Idioma, moeda e primeiro dia da semana são definidos uma vez, junto da conta, e não durante o primeiro lançamento.

**Hipótese para o Klipper:** oferecer um conjunto inicial opcional, localizado para pt-BR, mas gerenciá-lo integralmente em Configurações. A escolha deve gerar categorias editáveis próprias, não uma taxonomia “especial” impossível de ajustar.

### ezBookkeeping — conta, categoria e movimento preenchidos

- A lista de contas começa vazia, mas a criação manual reúne nome, tipo, ícone, cor, moeda, saldo e instante do saldo. Ao salvar, a conta aparece na lista com saldo e link direto à sua lista de movimentos; a alteração inicial de saldo é lançada no histórico como evento próprio.
- Categorias ficam em **Configurações > Dados base**, fora do formulário financeiro. Ao carregar o conjunto padrão, a tela mostra tipos de movimento (despesa, receita e transferência), categorias primárias e abas para cada pai. Selecionar `Alimentação e Bebidas`, por exemplo, revela as filhas da categoria em uma tabela própria.
- O formulário de movimento separa despesa, receita e transferência. Para despesa, mantém juntos valor, categoria, conta e data/hora; localização, tags, descrição e imagem são complementares. Conta e categoria assumem valores recentes, mas seguem visíveis e substituíveis.
- A lista de movimentos combina período, tipo, busca textual, totalizadores e importação. Uma busca aplicada entra na URL junto do intervalo (`keyword` e modo de correspondência), preservando o contexto e tornando-o compartilhável/restaurável.
- A importação é uma jornada explícita. Para formatos próprios, ela mostra envio, mapeamento de colunas, revisão/modificação e conclusão; para formatos nativos, o mapeamento é omitido. A prévia do assistente separa tipo de origem, formato, codificação e método de tratamento antes de aceitar o arquivo.
- Nesta rodada não houve envio concluído de arquivo: o conector de navegador não expôs o seletor oculto do assistente local. Portanto, regras de deduplicação e edição em lote ainda precisam de observação com arquivo sintético.

**Hipótese para o Klipper:** a conta deve ter um ponto de saldo inicial datado e histórico explícito; a lista de movimentos deve serializar filtros relevantes na URL. O Klipper não deve copiar a densidade de campos do formulário: no mobile, valor, conta, categoria e data ficam no primeiro plano; o restante é progressivo.

### ezBookkeeping — contraste na largura móvel (390 px)

- A navegação principal recolhe para um botão de menu, mas a lista conserva sua tabela de seis colunas. A própria lista passa a exigir rolagem horizontal para alcançar conta, tags e descrição.
- Busca, intervalo, totais e botão de adicionar continuam visíveis acima da tabela. O modal de importação abre centralizado, mas o seletor de tipo de arquivo fica comprimido quando há duas colunas de opções.

**Decisão para o Klipper:** reter filtros no topo e o acesso direto ao lançamento, mas não transportar a tabela para o mobile. Um movimento deve ser um cartão/lista de duas linhas: categoria e descrição, valor, conta e data; filtros avançados entram em folha própria. A revisão de importação deve usar seleção por linhas, não grade horizontal.

### Cashew — início em estado vazio

- A tela inicial expõe uma ação global de adicionar transação, independente da navegação lateral.
- A navegação torna visíveis, no mesmo nível, transações, contas, orçamento, metas, empréstimos, assinaturas, agendados, calendário e registro de atividade.
- O estado sem dados mantém os próximos destinos acionáveis em vez de exibir somente uma mensagem vazia.

**Hipótese para o Klipper:** o lançamento deve ter ponto de entrada global, particularmente no mobile; o dashboard vazio deve oferecer próximos passos claros sem competir com a leitura financeira quando houver dados.

### Cashew — onboarding orientado à primeira utilidade

- A experiência web abre uma apresentação curta antes do conteúdo. A primeira mensagem explica o benefício de registrar movimentos; a segunda apresenta orçamento mensal como controle de ritmo, com data de início e moeda editáveis; a conclusão oferece sincronização externa ou continuação sem login.
- A navegação já fica visível durante a introdução: transações, contas, orçamentos, metas, empréstimos, assinaturas, agendados, calendário e atividade. A promessa de produto é ampla, mas a primeira ação permanece ligada a transações.
- A opção de não sincronizar é explícita. Não foi iniciado login externo nem concedida conexão a conta de terceiros.

**Hipótese para o Klipper:** o primeiro uso pode explicar o valor em poucos passos e deixar sincronização como escolha posterior. Para o orçamento, o vocabulário de “ritmo” é mais acionável do que somente “limite mensal”.

## Trilhas de pesquisa e decisão

| Trilha | Perguntas a responder | Produtos de maior evidência | Saída prevista |
|---|---|---|---|
| Categorias e Configurações | Como criar, localizar, ordenar, ocultar e associar pai/filha sem perder contexto? | ezBookkeeping, Cashew | spec de árvore fixa de dois níveis + gestão em Configurações |
| Lançamento rápido mobile | Quanto tempo e quantos toques até salvar? Valor vem antes da descrição? Como cancelar e desfazer? | Cashew | folha móvel, “+” central e critérios de ≤ 4 ações |
| Movimento pós-importação | Como chegar às linhas importadas, filtrar, corrigir em lote e retornar ao contexto? | ezBookkeeping, Sure | filtros persistentes, deep link de revisão e desfazer |
| Painel e alarmes | Qual leitura domina? O que some sem dados? Quando um alerta vira ação? | Sure, Cashew | painel de patrimônio, evolução e alarmes acionáveis |
| Contas e orçamento | Como agrupar, datar saldo, abrir detalhe, mostrar histórico e ritmo diário? | Sure, ezBookkeeping, Cashew | detalhe de conta e orçamento orientado ao disponível diário |

## Decisões já preservadas

- O Klipper mantém sua direção náutica, tokens, tipografia e ícones Phosphor.
- Nenhuma paleta, texto, ícone, estrutura de arquivo ou asset de referência é transplantado.
- Componentes de apresentação podem variar entre desktop e mobile apenas quando a interação realmente muda; regras e dados ficam nos composables compartilhados.
- Cor semântica no Klipper continua reservada a ação, alerta e estado significativo.

## Próximas observações

1. Concluir o ambiente descartável do ezBookkeeping e carregar o conjunto padrão de dados sintéticos.
2. Percorrer categorias e configurações em desktop e mobile.
3. Percorrer lançamento rápido, cancelamento e desfazer no Cashew.
4. Percorrer importação, busca, filtro e correção em lote no ezBookkeeping e Sure quando disponíveis.
5. Registrar capturas e converter os achados em specs de implementação do Klipper.
