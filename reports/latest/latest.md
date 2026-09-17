# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `e0f07a0b20f4e373552e194e387f6750449c2e45` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | critical |
| Segurança | low |

## Possible Regressions

- **FIN-004** — medium → critical: apps/klipper-web/pages/dashboard.vue:211 — const spentRatio = computed(() => totalCredits.value > 0 ? totalDebits.value / totalCredits.value : 0) ainda retorna 0 em vez de null quando não há receita no ciclo, mesmo existindo pctOfIncome (apps/klipper-web/composables/useDashboardKpis.ts:24-27) que resolve exatamente esse caso e já está importado/usado no mesmo arquivo para fixoPct/cartaoPct (dashboard.vue:226-227). InstrumentReadout.vue:20,36-38 tem um estado 'sem dado' dedicado (hasRatio / data-testid=readout-no-budget, texto 'Sem orçamento definido') que este spentRatio poderia acionar e não aciona. Não existe apps/klipper-web/pages/__tests__/dashboard.test.ts cobrindo este computed — confirmado por busca direta no diretório de testes.
- **FIN-007** — medium → critical: apps/klipper-api/app/services/portfolio_service.rb:16 — pct = total_cost.positive? ? (type_cost / total_cost * 100).round(1) : 0.0 ainda zera a porcentagem de todos os tipos de investimento sempre que o custo líquido total da carteira é zero ou negativo, mesmo havendo posições reais. apps/klipper-api/spec/services/portfolio_service_spec.rb:55-70 é o único cenário com venda (buy+sell) e resulta em total_cost positivo (520.0) — nenhum caso de teste cobre total_cost líquido zero ou negativo.
- **FIN-009** — low → critical: apps/klipper-api/app/services/reimbursement_coverage_calculator.rb:50 — coverage_pct = spent.positive? ? (reimbursed / spent * 100).round(1) : nil não limita o valor quando reimbursed > spent no mês de referência. apps/klipper-api/spec/services/reimbursement_coverage_calculator_spec.rb não tem nenhum caso com reimbursed > spent no mês corrente — os cenários com percentuais altos (linhas 68-87) usam reimbursed sempre menor que spent.
- **FIN-005** — medium → critical: apps/klipper-api/app/services/pdf_adapters/btg_extrato_adapter.rb:15-19 documenta explicitamente que a suposição de que a coluna 'Movimentação R$' já vem com o sinal correto (sem inversão) nunca foi confirmada contra um débito real. apps/klipper-api/spec/services/pdf_adapters/btg_extrato_adapter_spec.rb (linhas 28-109) só exercita lançamentos 'RENDIMENTOS' (crédito) — nenhum exemplo sintético nem fixture com valor de débito.

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| FIN-001 | 🟡 medium | finance | 250 | InstrumentReadout continua com o rótulo de razão ('% da renda') e o texto de estado nulo hardcoded para o caso do dashboard, então orcamento.vue exibe a leitura textual errada para uma métrica que na verdade mede % do orçamento alocado, não % da renda. |
| ARCH-011 | 🟠 high | architecture | 135 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) são singletons globais sem nenhum teste direto — open()/close()/payload reset em useModal e o auto-dismiss via setTimeout em useToast só são exercitados incidentalmente através dos testes de componentes individuais que os mockam, nunca testados isoladamente. |
| FIN-004 | 🔴 critical | finance | 122.5 | O computed spentRatio do hero do dashboard continua retornando 0 em vez de null quando não há receita no ciclo, fazendo InstrumentReadout renderizar uma barra 0%-preenchida como se fosse dado real em vez do estado 'sem dado' — a mesma proporção financeira sem cobertura de borda que a Regra de Ouro trata como crítica, e o helper que já corrige esse caso (pctOfIncome) está no mesmo arquivo sem ser usado aqui. |
| ARCH-012 | 🟠 high | architecture | 112 | Como as três chamadas de fetch em relatorios.vue (e o padrão análogo em dashboard.vue) correm em paralelo sobre o mesmo isLoading, a primeira a resolver derruba isLoading para false enquanto as outras ainda estão em voo — nesse intervalo o template já trata os refs ainda nulos (`monthly`, `netWorth`) como carregados e renderiza `formatBRL(0)` (R$ 0,00) como se fosse o total real, em vez do placeholder '—'. |
| ARCH-004 | 🟡 medium | architecture | 60 | Quatro componentes Vue de entrada/edição de dados financeiros continuam sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-005 | 🟡 medium | architecture | 52.5 | Cinco páginas centrais do Wealth OS continuam sem nenhum teste de página. |
| FIN-008 | 🟡 medium | finance | 48 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o item de rastreabilidade da checklist financeira do projeto. |
| ARCH-009 | 🟡 medium | architecture | 32 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) não tem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-013 | 🟡 medium | architecture | 30 | A lógica de sinal buy/sell (documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada) tem uma terceira reimplementação não coberta pelo teste de paridade existente entre signed_cost e signed_cost_sql, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste de paridade acuse. |
| FIN-007 | 🔴 critical | finance | 30 | PortfolioService#allocation reporta 0.0% de alocação para todos os tipos de investimento sempre que o custo líquido total da carteira é zero ou negativo, mesmo havendo posições reais, e nenhum teste cobre esse caso de borda — violação direta da regra de cálculo financeiro sem teste de borda. |
| ARCH-014 | 🟡 medium | architecture | 20 | O padrão visual de campo com select (label, wrapper, seta customizada) é reimplementado em CSS scoped duplicado em pelo menos quatro modais de entidade diferentes dos de lançamento, então qualquer ajuste visual (ex: acessibilidade do caret, espaçamento) precisa ser replicado manualmente em cada arquivo e tende a divergir. |
| ARCH-006 | 🟡 medium | architecture | 20 | ReportsController mistura dois padrões arquiteturais no mesmo arquivo: metade das actions agrega dados financeiros inline, a outra metade delega a Calculator services. |
| FIN-009 | 🔴 critical | finance | 18 | ReimbursementCoverageCalculator pode reportar coverage_pct acima de 100% quando o valor reembolsado excede o gasto do mês de referência, e esse caso de borda de uma proporção financeira nunca é exercitado por teste. |
| SEC-003 | 🟢 low | security | 18 | As 4 advisories (1 low, 3 high) reportadas anteriormente em devDependencies transitivas do toolchain de build já caíram para apenas 1 advisory low (esbuild) em cada um dos dois frontends, restando só o `npm audit fix` final; o lado Ruby/Rails segue limpo em bundler-audit e brakeman. |
| ARCH-015 | 🟢 low | architecture | 12 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| ARCH-008 | 🟡 medium | architecture | 12 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) segue sem qualquer rate limiting, diferente de todas as outras actions de autenticação não-autenticadas. |
| FIN-005 | 🔴 critical | finance | 4.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição que o próprio autor documentou como não verificada, e nenhum teste cobre um débito real — dado de patrimônio de import bancário sem cobertura de caso normal (débito), tratado como crítico por definição. |
| SEC-006 | 🟢 low | security | 2 | O access token JWT continua em cookie legível por JavaScript (sem httpOnly), mas a CSP com nonce por request já implementada reduz significativamente o raio de um XSS futuro em relação ao estado anterior; nenhum sink de XSS explorável foi encontrado nesta auditoria. |
