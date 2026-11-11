# Roadmap consolidado — Klipper

Ponto único para escolher a próxima frente e acompanhar seu estado. Criado em 2026-10-30 a partir dos planos existentes; status históricos não são comprovação de que o código atual satisfaz todos os critérios. As specs, auditorias, ADRs e decisões originais continuam disponíveis e não devem ser descartadas.

## Como usar

- Atualizar aqui o estado e a evidência de cada frente ao encerrá-la; manter requisitos e decisões detalhados nas fontes vinculadas. Não iniciar duas fontes concorrentes de prioridade.
- Estado: **pendente**, **parcial**, **concluído com evidência** ou **a verificar**. Ausência de evidência é “a verificar”, não “concluído”.
- Uma fatia por PR, TDD e critérios de aceite; aguardar CI do PR e da main. Código e regras financeiras prevalecem sobre descrições visuais antigas. A ordem e as regras de domínio aprovadas estão no [plano de domínio](docs/domain-research/05-plano-implementacao.md) e nas suas specs.
- Respeitar [processo](CLAUDE-process.md), [sala limpa e licenças](docs/domain-research/05-plano-implementacao.md#política-de-código-de-terceiros-2026-10-17) e decisões de produto. Antes de implementar uma tarefa, conferir estado no código e em PRs.

## Ordem de execução

| Ordem | Frente | Estado inicial | Dependência e evidência exigida | Fonte |
|---|---|---|---|---|
| 0 | CI Ruby e referência do alfa | CI verde na main; #189 e #201 integrados | CI comprovado: workflow `CI` com `success` em `a05ef68` (merge #220, 2026-11-10). Falta executar jornada sintética em desktop, 390 px e teclado. | [Plano UX — etapa 0](docs/ux-research/06-plano-implementacao.md#0-referência-e-preparação) |
| 1 | Navegação e lançamento manual | Parcial; aceite a verificar; “+” mobile em #191, proteção de rascunho em #193 e fatia mobile 1 (alvos de 44 px, Salvar fixo no rodapé, “Mais” como diálogo) com evidência na [matriz 11](docs/ux-research/11-matriz-de-avaliacao.md#evidência-no-klipper) | Validar categoria e contratos existentes; concluir estados, desfazer e as fatias mobile 2 (gestos dentro da tela, nunca nas bordas do sistema) e 3 (revisão por tela). Pendente: rodar `npm run test:mobile` no CI e validar no aparelho. | [Etapa 1](docs/ux-research/06-plano-implementacao.md#1-navegação-e-lançamento--fatia-2), [spec](docs/ux-research/05-specs/02-lancamento-rapido.md) |
| 2 | Movimento | Parcial; núcleo financeiro D1–D3 integrado em #181 | Conferir filtros, contexto, lista mobile e ações em lote transacionais no fluxo real. O #203 resolveu a dupla contagem histórica C-4; bloquear lançamento manual anterior à abertura e alertar na importação continuam pendentes. | [Etapa 2](docs/ux-research/06-plano-implementacao.md#2-movimento--fatia-4), [spec](docs/ux-research/05-specs/03-transacoes.md) |
| 3 | Detalhe de conta | Parcial; rota e histórico corrigidos em #203; aceite a verificar | Validar D1 e D2, saldo explicável e contrato real de histórico. Cartão depende de D4. | [Etapa 3](docs/ux-research/06-plano-implementacao.md#3-detalhe-de-conta--fatia-4-dependente-de-d1d2), [spec](docs/ux-research/05-specs/04-contas.md) |
| 4 | Painel | Parcial; aceite a verificar | Saldo/patrimônio corretos; D4 para vencimento de cartão. Dados reais e falhas isoladas. | [Etapa 4](docs/ux-research/06-plano-implementacao.md#4-painel--fatia-3-conforme-dependências-de-domínio), [spec](docs/ux-research/05-specs/01-painel.md) |
| 5 | Liberação alfa | Pendente de comprovação | Jornada integrada, exportação, segurança operacional e restauração de backup. Apenas lançamentos manuais no alfa D1–D3. | [Operação segura](docs/alpha/01-operacao-segura.md) |

A ordem de UX acima não antecipa regras de domínio: a decisão aprovada é D1 antes de D0; os demais incrementos seguem dependências do [plano de domínio](docs/domain-research/05-plano-implementacao.md#sprints). O documento UX preserva um aviso histórico de bloqueio das Fatias 3–7; consulte as dependências específicas aprovadas no plano de domínio antes de abrir cada fatia, sem assumir que a aprovação do plano significa implementação concluída.

## Auditoria objetiva — 2026-11-02, atualizada em 2026-11-10

As linhas de MCP descrevem a sessão de 2026-11-02; as de checkout, sequência e CI foram reconferidas em 2026-11-10.

| Verificação | Evidência observada | Estado |
|---|---|---|
| MCP ai-memory | Ferramentas disponíveis nesta sessão; `memory_recent` e `memory_status` responderam para este projeto (59 páginas vigentes, 52 sessões, 19.363 observações). | Conexão real confirmada. |
| MCP Serena | Configuração local encontrada em `~/.codex/config.toml` e memórias do projeto em `.serena/memories/`; nenhuma ferramenta Serena foi carregada nesta sessão, portanto não foi possível confirmar conexão real aqui. | Configurado localmente; conexão nesta sessão não confirmada. |
| MCP GitHub | Consultas de PR e status de commit responderam; #181 e #203 constam como merged. | Conexão real confirmada. |
| MCPs para validação UX | Os relatórios de Actual, Cashew e Firefly registram Playwright MCP e navegador manual indisponíveis e axe não executado. Nenhum Playwright MCP foi carregado nesta sessão. | Bloqueio de instrumentação; não confundir com falha do produto. |
| Checkout / `main` | Checkout disponível em `11.01-Klipper`, branch `main` alinhada a `origin/main`, commit `a05ef68` (merge #220) em 2026-11-10. | Referência local confirmada. |
| PR #181 e sequência | #181 integrou o núcleo financeiro D1–D3 em 2026-10-29. Depois entraram o plano UX (#26f59f9), #189 (Ruby CI), #190 (roadmap consolidado), #191 (navegação mobile), #193 (rascunho), #194–195 (processo/CI de docs), #198 (backup), #200 (benchmark UX), #201 (CI main) e #203 (C-4, rota/histórico e rótulos). Após a auditoria: #206 (acesso pelo celular — API na mesma origem e ícones do PWA), #216 (Rails 8.1.4.1, GHSA-5957), #219 (`RAILS_ALLOWED_HOSTS` com os hosts do front repassados pelo proxy) e #220 (passo “Criar o primeiro orçamento”). | Histórico conferido no primeiro pai de `main`. |
| Estado posterior de C-4 | #203 corrige saldo e histórico para ignorar lançamentos anteriores à abertura e inclui auditoria somente leitura para avaliar abertura migrada. Recusa de lançamento manual retroativo e aviso na importação seguem fora do escopo entregue. | Correção parcial concluída; pendência explícita. |
| CI atual | `gh run list --branch main`: workflow `CI` com `success` em `a05ef68` (2026-11-10). O endpoint de *commit status* só mostra Vercel porque o Actions publica *check runs*, não status. No mesmo commit, o relatório de auditoria automático falhou no agente `architecture` (run `42755601409`), sem relação com o código. O backup agendado de produção continua falhando todo dia (última execução em 2026-11-09) com `Configuração de backup ausente: DATABASE_URL`. | CI confirmado; backup de produção sem configuração. |

**Prioridade nova (Roberto, 2026-11-02): o Klipper funcionando no celular, o quanto antes, para uso durante uma viagem.** Passa à frente de todas as frentes abaixo. O alinhamento detalhado foi feito com o Codex numa tarefa na nuvem (`01a18bef-…`) que não está no repositório. O acesso pelo celular entrou no #206 e os hosts do proxy no #219; falta comprovar o uso no aparelho com a API de produção.

**Ordem anterior do roadmap, agora abaixo da prioridade mobile:** (0) CI em `main` já comprovado; (1) concluir jornada UX com Playwright/navegador e axe disponíveis; (2) validar movimento e detalhe de conta ponta a ponta; (3) então avançar painel e liberação alfa, incluindo segurança operacional/restauração. Manter o bloqueio retroativo C-4 visível até existir decisão de produto e critério de aceite para escrita/importação. Não há evidência nesta auditoria para mudar a ordem aprovada do domínio ou declarar liberação do alfa.

## Domínio e produto — mapa de trabalho

Cada status abaixo deve ser reconciliado com código, testes e decisões antes de planejamento. O código existente pode ser parcial; nomes de serviços em specs não garantem sua existência.

| Frente | Escopo e vínculo | Estado |
|---|---|---|
| D0–D3 | Fundamentos, contabilidade de receitas/despesas, saldo/conferência e transferência/estorno. D1 antes de D0. | Parcial; verificar por critério. |
| D4 | Ciclo de cartão, vencimento, fatura e parcelas. | A verificar; dependência para alertas de cartão. |
| D5 | Importação, conciliação, idempotência, mapeamento e desfazer. Há CSV/PDF existente; não presumir cumprimento integral das novas specs. | Parcial; fora do alfa manual. |
| D6–D8 | Recorrências, regras e aprendizado, orçamento e ritmo. | A verificar; ver specs e ordem do domínio. |
| Patrimônio | Posições, preço de mercado, desempenho, projeção e runway dependem dos contratos e dados confiáveis. Módulo P depois de D1–D8 e dos cenários P0 aprovados. | Planejado / a verificar. |
| Kakebo | Ciclo mensal e resumo por pilar, começando pela persistência no backend. | Especificado, pendente segundo [spec](docs/KAKEBO.md) e [roadmap histórico](ROADMAP_KLIPPER_WEALTH_OS.md#feature-de-produto--método-kakebo). |

Detalhes, critérios e decisões: [D0–D8 e módulo P](docs/domain-research/05-plano-implementacao.md#sprints), [specs de domínio](docs/domain-research/03-specs/), [fronteira patrimonial](docs/domain-research/03-specs/20-fronteira-do-nucleo-e-modulo-patrimonio.md) e [Kakebo](docs/KAKEBO.md).

## Transversais e dívida

| Área | Próxima ação | Origem |
|---|---|---|
| Segurança e operação | Conferir isolamento por usuário, recuperação, backup, monitoramento e pendências das auditorias antes de liberar participantes. | [Alfa seguro](docs/alpha/01-operacao-segura.md), [auditorias](docs/security/), [backlog histórico](ROADMAP_KLIPPER_WEALTH_OS.md#backlog-priorizado-de-execução-produto--segurança-auditorias-2026-07-27-a-2026-07-29) |
| Acessibilidade e UX | Revisar contraste, foco, estados de tela, mobile por tarefa e invalidação após alterações; verificar quais itens UX-R1–R7 ainda se aplicam. | [Revisão UX-R](ROADMAP_KLIPPER_WEALTH_OS.md#revisão-de-uxproduto--2026-09-16-7-pontos), [matriz UX](docs/ux-research/11-matriz-de-avaliacao.md) |
| Arquitetura, privacidade e performance | Reconciliar C1–C3, A1–A6, M1–M6 e B1–B3 com o código; atenção a sessão, fila offline, importação assíncrona e auditoria de exportação. Não presumir que itens listados no plano de setembro estão abertos ou concluídos. | [Auditoria de setembro](PLANO_EXECUCAO_KLIPPER_2026-09-14.md) |
| Design | Preservar direção náutica e verificar telas/tokens e estados contra o produto atual; não tratar o mockup histórico como substituto de regras financeiras ou specs atuais. | [Redesign histórico](docs/design/ROADMAP_REDESIGN_KLIPPER.md), [tokens](docs/ux-research/04-design-tokens.md) |
| Pesquisa UX | Ciclos e critérios de acessibilidade/integração ainda precisam de evidência no Klipper. | [Matriz](docs/ux-research/11-matriz-de-avaliacao.md), [observação](docs/ux-research/09-observacao-ao-vivo.md) |

## Fontes e precedência

1. Decisões explícitas posteriores do usuário e ADRs aplicáveis.
2. Para regras e sequência financeira: plano e specs de domínio; para execução das jornadas: plano UX, subordinado ao domínio. Não alterar decisões aprovadas por mera consolidação.
3. Este arquivo acompanha prioridades e evidências; requisitos detalhados permanecem nas specs. Atualizar ambos quando uma decisão mudar.
4. [Roadmap de produto e segurança](ROADMAP_KLIPPER_WEALTH_OS.md), [plano de setembro](PLANO_EXECUCAO_KLIPPER_2026-09-14.md) e [redesign](docs/design/ROADMAP_REDESIGN_KLIPPER.md) preservam histórico, achados, critérios e decisões; datas e status ali podem estar defasados. Não apagar IDs sem mapear cada um.

## Fora do escopo atual

Não reabrir o fluxo operacional de reembolsos de saúde recusado pelo usuário: esse domínio pertence ao Gestor-Reembolsos. Tema claro e envelope completo não fazem parte da execução atual; ver decisões nas fontes históricas e de domínio.
