# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `b5e90d644157454d1e751105b3e425777a27aef1` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | high |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| FIN-004 | 🟡 medium | finance | 500 | O computed spentRatio do hero do dashboard continua retornando 0 em vez de null quando não há receita no ciclo, fazendo InstrumentReadout renderizar uma barra 0%-preenchida como se fosse um dado real em vez do estado 'sem dado'. |
| FIN-001 | 🟡 medium | finance | 250 | InstrumentReadout continua com o rótulo de razão ('% da renda') e o texto de estado nulo ('Sem orçamento definido') hardcoded, então orcamento.vue exibe a leitura textual errada para uma métrica que na verdade mede % do orçamento alocado, não % da renda. |
| ARCH-003 | 🟠 high | architecture | 128 | A fórmula de patrimônio líquido continua duplicada entre NetWorthSnapshotService e ReportsController#net_worth, apesar do ADR proposto para unificá-la já existir. |
| ARCH-004 | 🟡 medium | architecture | 60 | Quatro componentes Vue de entrada/edição de dados financeiros (nova conta, novo membro, editar reembolso, e o wrapper ModalMount) continuam sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-005 | 🟡 medium | architecture | 52.5 | Cinco páginas centrais do Wealth OS (dashboard, contas, investimentos, orçamento, portadores) continuam sem nenhum teste de página. |
| ARCH-009 | 🟡 medium | architecture | 40 | O composable de focus trap e o componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) seguem sem nenhuma cobertura de teste, direta ou indireta. |
| SEC-003 | 🟡 medium | security | 30 | apps/klipper-web segue com as mesmas 4 advisories (1 low, 3 high/moderate) em devDependencies transitivas do toolchain de build, não embarcadas no bundle de produção mas exercitadas em todo `npm run dev`/CI; e, diferente de quebec-web, o job `web` do CI não tem nenhum gate de `npm audit`, então uma futura advisory crítica no mesmo toolchain não bloquearia o merge. |
| ARCH-006 | 🟡 medium | architecture | 25 | ReportsController mistura dois padrões arquiteturais no mesmo arquivo: metade das actions agrega dados financeiros inline, a outra metade delega a Calculator services. |
| FIN-007 | 🟡 medium | finance | 24 | PortfolioService#allocation reporta 0.0% de alocação para todos os tipos de investimento sempre que o custo líquido total da carteira é zero ou negativo, mesmo havendo posições reais, sem nenhum teste cobrindo esse caso. |
| FIN-009 | 🟢 low | finance | 24 | ReimbursementCoverageCalculator pode reportar coverage_pct acima de 100% quando o valor reembolsado excede o gasto do mês de referência, e esse caso nunca é exercitado por teste. |
| ARCH-008 | 🟡 medium | architecture | 12 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm (já testado após ARCH-002), mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. |
| FIN-008 | 🟡 medium | finance | 12 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o item de rastreabilidade da checklist financeira do projeto. |
| SEC-005 | 🟢 low | security | 8 | PATCH /api/v1/password_resets/:token (redenção do token de reset) segue sem rate limiting, ao contrário de toda outra action de autenticação não-autenticada; o token é assinado/expirável via `generate_token_for` do Rails (não um código curto adivinhável), então a exploração prática é limitada — é uma lacuna de defesa em profundidade/carga de banco, não um caminho de força bruta realista hoje. |
| FIN-005 | 🟢 low | finance | 6 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição que o próprio autor documentou como não verificada, e nenhum teste cobre um débito real — risco aceito e já documentado no roadmap, mas ainda sem cobertura. |
| SEC-006 | 🟢 low | security | 4 | O access token JWT (15 min de validade) continua em um cookie legível por JavaScript no cliente, diferente do refresh token que é HttpOnly, e não há CSP configurada no Nuxt para reduzir o raio de um XSS futuro; isso é defesa em profundidade insuficiente ainda que nenhum sink de XSS explorável tenha sido encontrado nesta auditoria (os 2 usos de v-html em components/layout/MobileNav.vue interpolam apenas strings SVG literais hardcoded no componente, sem entrada de usuário). |
