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
| 0 | CI Ruby e referência do alfa | Parcial; [PR #189](https://github.com/Borussia80/Klipper/pull/189) aberto | Confirmar CI na main; executar jornada sintética em desktop, 390 px e teclado. | [Plano UX — etapa 0](docs/ux-research/06-plano-implementacao.md#0-referência-e-preparação) |
| 1 | Navegação e lançamento manual | Parcial; aceite a verificar | Validar categoria e contratos existentes; “+” mobile, rascunho, acessibilidade e desfazer. | [Etapa 1](docs/ux-research/06-plano-implementacao.md#1-navegação-e-lançamento--fatia-2), [spec](docs/ux-research/05-specs/02-lancamento-rapido.md) |
| 2 | Movimento | Parcial; aceite a verificar | D1 e D2; filtros, contexto, lista mobile e ações em lote transacionais. | [Etapa 2](docs/ux-research/06-plano-implementacao.md#2-movimento--fatia-4), [spec](docs/ux-research/05-specs/03-transacoes.md) |
| 3 | Detalhe de conta | Parcial; aceite a verificar | D1 e D2; saldo explicável e contrato real de histórico. Cartão depende de D4. | [Etapa 3](docs/ux-research/06-plano-implementacao.md#3-detalhe-de-conta--fatia-4-dependente-de-d1d2), [spec](docs/ux-research/05-specs/04-contas.md) |
| 4 | Painel | Parcial; aceite a verificar | Saldo/patrimônio corretos; D4 para vencimento de cartão. Dados reais e falhas isoladas. | [Etapa 4](docs/ux-research/06-plano-implementacao.md#4-painel--fatia-3-conforme-dependências-de-domínio), [spec](docs/ux-research/05-specs/01-painel.md) |
| 5 | Liberação alfa | Pendente de comprovação | Jornada integrada, exportação, segurança operacional e restauração de backup. Apenas lançamentos manuais no alfa D1–D3. | [Operação segura](docs/alpha/01-operacao-segura.md) |

A ordem de UX acima não antecipa regras de domínio: a decisão aprovada é D1 antes de D0; os demais incrementos seguem dependências do [plano de domínio](docs/domain-research/05-plano-implementacao.md#sprints). O documento UX preserva um aviso histórico de bloqueio das Fatias 3–7; consulte as dependências específicas aprovadas no plano de domínio antes de abrir cada fatia, sem assumir que a aprovação do plano significa implementação concluída.

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
