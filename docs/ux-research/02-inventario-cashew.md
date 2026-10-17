# 02 — Inventário: Cashew

**Licença:** GPL-3.0 → **sala limpa.** Nada de código Dart, assets ou estrutura do repositório.
**Papel no Klipper:** fluxos mobile — lançamento rápido, navegação inferior, orçamento com limite por categoria,
gestos. **Interações sim, paleta colorida não.**

## Estado da observação

| Fonte | Situação |
|---|---|
| PWA em execução | **Não observada nesta sessão.** O README aponta o web app público em `https://budget-track.web.app/`; a URL do pedido ficou como placeholder. É um app Flutter web — não dá para ler por fetch de texto, precisa de navegador |
| Prints (`prints/cashew/`) | **Não existem** |
| Documentação pública | Lida: README (só o texto), listagem da App Store |

Mesma convenção do inventário do Sure: **[DOC]** = afirmado na documentação; **[A OBSERVAR]** = hipótese.

## O que a documentação afirma

- **[DOC]** Orçamentos com **período personalizável** (diário, semanal, mensal ou sob medida — ex.: orçamento de
  viagem), **limite por categoria**, histórico de orçamentos anteriores, metas de gasto ou de poupança.
- **[DOC]** Tipos de transação: futuras, assinaturas, recorrentes, dívidas (emprestei/peguei emprestado).
- **[DOC]** Títulos que **se associam automaticamente a uma categoria** (o mesmo nome cai na mesma categoria).
- **[DOC]** Busca com filtros; **edição e exclusão em lote**.
- **[DOC]** Várias contas e moedas, troca rápida de conta na tela inicial.
- **[DOC]** Tela inicial configurável; gráficos interativos; layout adaptável web/celular.
- **[DOC]** Importação CSV e Google Sheets; criação de transação por link de app.
- **[DOC]** Releases recentes: registro de atividade (transações apagadas/alteradas), tela de agendadas
  refeita, atalho para duplicar transação, opção de vibração (haptics).
- **[DOC]** Design **Material You**, cor de destaque personalizável, claro/escuro.
- **[DOC]** O README não cita bibliotecas de ícones nem fontes; menciona apenas busca entre vários ícones ao criar
  categoria.

## Fluxos a observar (o que de fato interessa)

| # | Fluxo | Perguntas para a observação (390 px) |
|---|---|---|
| C1 | **Lançamento rápido** | Quantos toques do ícone "+" até salvar um gasto de R$ 23,50 no mercado? O valor vem primeiro? Teclado numérico próprio ou do sistema? Categoria é grade de ícones? Data padrão = hoje? Dá para salvar sem preencher descrição? |
| C2 | **Navegação inferior** | Quantos destinos? Onde fica o "+"? O que acontece ao tocar duas vezes no destino ativo? |
| C3 | **Orçamento por categoria** | Como mostra "quanto ainda posso gastar hoje"? Marcador de "onde eu deveria estar" no mês? O que muda visualmente ao estourar? |
| C4 | **Gestos na lista** | Arrastar para o lado apaga? Tem desfazer? Toque longo seleciona para lote? |
| C5 | **Agendadas / assinaturas** | Como lista o próximo vencimento? Confirmação manual ou lançamento automático? |
| C6 | **Associação título → categoria** | Sugere enquanto digita? Aprende com a correção? |
| C7 | **Estado vazio do primeiro uso** | O que pede primeiro? |

## O que descartar de antemão (pelo papel definido no pedido)

- **Paleta colorida e cor de destaque personalizável**: categorias multicoloridas e acento escolhido pelo usuário
  contrariam a regra de cor do Klipper e a direção náutica. No Klipper, a cor da categoria fica restrita ao
  ícone/marcador de identificação e a gráficos de composição, e nunca concorre com condição anormal.
- **Material You como linguagem**: o Klipper não adota a linguagem visual do Material; só os padrões de interação
  que são genéricos de mobile (botão de ação, folha inferior, arrastar para ação com desfazer).
- **Login Google / backup Google Drive**: fora do escopo e do modelo de dados do Klipper.
