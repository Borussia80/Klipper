# 08 — Revisão UI/UX alfa

## Resumo

1. O ciclo brasileiro de importar e revisar antes de gravar é uma vantagem concreta do Klipper; deduplicação ainda é requisito a validar, não uma capacidade comprovada.
2. O painel atual explica o mês, mas patrimônio e sua evolução continuam deslocados para Relatórios.
3. Sete referências foram observadas em execução. Sure, Cashew, Firefly III, Wealthfolio e Ghostfolio permanecem como UX observável; ezBookkeeping e Actual Budget tiveram leitura técnica MIT registrada no protocolo 12.
4. A maior quebra do ciclo é chegar da importação à categorização e à conferência sem filtros e atalhos suficientes.
5. No celular falta o “+” global: lançamento manual começa por uma rota e abre formulário longo.
6. Contas agrupam corrente e cartão, porém não oferecem detalhe, histórico de saldo nem sinal de atualização.
7. Orçamento informa gasto acumulado, mas não traduz claramente ritmo diário, disponível e estouro por prioridade.
8. Estados básicos existem em muitas telas, porém recuperação, feedback parcial e fluxos mobile não foram todos verificados em execução. O piloto confirmou que importação precisa tratar conta, categoria e data inválida como pendências recuperáveis.

## Achados priorizados

| Pri. | Tela | O que acontece / expectativa | Base da comparação | Esforço |
|---|---|---|---|---|
| P0 | Movimento após importar | A prévia permite selecionar e confirmar linhas, mas Movimento só filtra por tipo e mês. Quem precisa achar e corrigir itens importados espera busca e filtros por conta/categoria/portador, inclusive acesso direto da conclusão da importação. | Klipper já ganha com prévia; sem evidência no inventário de fluxo equivalente do Sure. | M |
| P0 | Navegação mobile / lançamento | A barra inferior tem Painel, Movimento, Orçamento, Investimentos e Mais; não há “+” global. Para registrar algo, a pessoa precisa achar Movimento e então Adicionar; o formulário é genérico, sem valor-primeiro, categorias frequentes ou teclado próprio. Esperado: ação de lançamento sempre alcançável e curta. | Especificação adotada; sem evidência no inventário de interface Sure. | L |
| P0 | Painel | A primeira leitura é resultado mensal; patrimônio e linha temporal estão em Relatórios. Para conferir números do mês e situação total, o usuário troca de tela. Esperado: patrimônio dominante, evolução, alarmes e mês na mesma leitura. | Documentação do Sure confirma painel com patrimônio e fluxo; especificação 01 detalha a adaptação própria. | L |
| P1 | Importar | Há boa revisão por linha, avisos e resultado com duplicatas, mas a confirmação não expõe categorização, regra reutilizável nem um caminho explícito para revisar “sem categoria”. Esperado: terminar a importação sabendo o que ainda pede classificação. | O piloto do ezBookkeeping confirmou que reimportação pode duplicar conteúdo sem aviso; Klipper deve tornar a decisão explícita. | M |
| P1 | Contas | A lista separa contas e cartões, mas não há subtotal por grupo, conta arquivada/defasada, página de detalhe, histórico de saldo nem transações filtradas daquela conta. Esperado: conferir saldo, data de atualização e origem das diferenças sem procurar em outra tela. | Dossiê do Sure comprova saldo datado/reconciliação e histórico; interface de contas do Sure: sem evidência no inventário. | L |
| P1 | Orçamento | Mostra livre, alocado e gasto, mas não “quanto por dia” nem marcador de ritmo; categoria sem limite e excesso não têm a hierarquia proposta. Esperado: saber imediatamente se ainda cabe gasto hoje e onde agir. | Sem evidência no inventário de tela Sure; especificação 05 define o comportamento desejado. | M |
| P1 | Categorias | Só há categoria de um nível, criada por modal; Configurações não oferece gestão. Após importar, nomes parecidos não podem ser organizados, ocultados ou mesclados. Esperado: árvore simples, busca e manutenção sem alterar lançamentos antigos. | Sem evidência no inventário de Sure; especificação 07. | L |
| P1 | Login/cadastro | Campos vazios podem receber tentativa sem mensagem local; a pessoa só descobre o que falta após nenhuma ação perceptível. Esperado: validação junto ao campo e CTA inequivocamente indisponível até o mínimo necessário. | Sem evidência no inventário de Sure. | S |
| P1 | Configurações | “API online” é apresentado como estado fixo e categorias não estão ali; a pessoa espera estado verificável e agrupamento de conta, dados e preferências. | Inventário Sure apenas sugere organização por seções; sem observação de interface. | S |
| P2 | Transações | Há seleção e exclusão em lote, mas exclusão exige confirmação e não oferece desfazer; em celular não há gesto nem edição em lote de categoria. Esperado: correção rápida e reversível de importações. | Sem evidência no inventário de Sure para gesto; especificação 03. | M |
| P2 | Feedback/carregamento | Skeletons, vazios e toasts já cobrem muitas telas, mas erros exibidos não trazem ação de repetir em todas elas e o painel agrega falhas de fontes distintas numa faixa. Esperado: falha localizada com nova tentativa, sem perder o restante. | Especificação 01; execução não verificada. | M |

## Não verificado

- Sure com dados preenchidos: painel de patrimônio, alertas, detalhe/histórico de conta, orçamento e movimentos ainda não foram percorridos ponta a ponta.
- Cashew com dados preenchidos em 390 px: lançamento, edição, cancelamento, desfazer, filtros e orçamento ainda não foram percorridos ponta a ponta.
- Actual Budget: o servidor local oficial completou importação e reimportação. Com mesclagem ativa, bloqueou duplicatas exatas e também a quase duplicata de mesma data/valor; o CSV revelou ainda que colunas sem semântica compatível precisam ser sinalizadas na prévia.
- Sucesso/erro real de upload, confirmação, transferência, retry, foco e leitor de tela ainda não foram executados em todos os apps. No ezBookkeeping, o fluxo foi concluído pela API local: conta de destino, categorias e data anterior ao saldo inicial produziram erros recuperáveis; uma nova importação inseriu novamente as linhas sem comparar seu conteúdo.
- `docs/ux-research/prints/` agora contém o CSV sintético do Lote 0; não há captura visual nova associada ao piloto.

## Backlog sugerido (ordem)

### P0 — fechar lacunas críticas antes da implementação ampla

1. **Sure preenchido:** criar contas, movimentos, orçamento e alertas sintéticos; registrar painel, detalhe de conta, histórico de saldo, filtros e estados de vazio/erro/sucesso em 1440 px e 390 px.
2. **Cashew preenchido:** registrar lançamento rápido, edição, cancelamento, desfazer, filtros, orçamento e navegação inferior em 390 px e desktop; medir toques até salvar.
3. **Matriz final:** confrontar os sete produtos por tarefa, separar evidência de hipótese e atualizar os critérios de aceite próprios do Klipper. Apps copyleft continuam como UX observável nesta fila; leituras MIT seguem classificadas como técnica/dirty no 12.

### P1 — implementação no Klipper, após a matriz final

4. Entregar filtros/busca e ação de categorizar pós-importação em Movimento.
5. Criar lançamento rápido mobile pelo “+” central, com recuperação após erro e desfazer.
6. Reorganizar Painel em torno de patrimônio, evolução, alarmes acionáveis e últimos lançamentos.
7. Implementar categorias em dois níveis e orçamento orientado a disponível/ritmo.
8. Criar detalhe de conta com saldo histórico, atualização e lista filtrada de lançamentos.

## Fontes lidas e limites

- Li `CLAUDE.md`, `CLAUDE-process.md`, `01`–`13` de `docs/ux-research/` e os relatórios do Lote 0. A classificação de cada fonte e a separação entre UX observável e análise técnica estão no `12`.
- Li as capturas disponíveis em `SCREENSHOTS_KLIPPER/` para painel, transações, contas e orçamento; não havia `docs/ux-research/prints/`.
- A observação ao vivo está registrada em `09-observacao-ao-vivo.md`; nenhum código, CSS, template ou asset dos apps copyleft foi aberto nesta fila.
