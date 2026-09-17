# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `a1a08c5acf5dd620ffbf9eac2174f856d3b600a5` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | medium |
| Segurança | medium |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-002 | 🟠 high | architecture | 450 | A lógica de validação e parsing de valores financeiros de useLancamentoForm, compartilhada pelos modais de novo e editar lançamento, continua sem teste unitário dedicado. |
| FIN-001 | 🟡 medium | finance | 250 | InstrumentReadout continua com o rótulo de razão e o texto de estado nulo hardcoded para o caso de dashboard, então orcamento.vue exibe a leitura textual errada para uma métrica que na verdade mede % do orçamento alocado. |
| ARCH-003 | 🟠 high | architecture | 128 | A fórmula de patrimônio líquido (contas + investimentos) continua duplicada entre NetWorthSnapshotService e ReportsController#net_worth em vez de reutilizar o service existente; já há ADR proposto (não implementado) descrevendo a extração. |
| FIN-004 | 🟡 medium | finance | 105 | O computed spentRatio do hero do dashboard continua retornando 0 em vez de null quando não há receita no ciclo, fazendo InstrumentReadout renderizar uma barra 0%-preenchida como se fosse um dado real em vez do estado "sem dado". |
| SEC-002 | 🟢 low | security | 80 | O endpoint não-autenticado /api/v1/health continua devolvendo `Rails.env` no corpo JSON, permitindo que qualquer chamador anônimo identifique se o alvo é produção/staging/desenvolvimento. |
| ARCH-004 | 🟡 medium | architecture | 60 | Quatro componentes Vue de entrada/edição de dados financeiros (nova conta, novo membro, editar reembolso, e o wrapper ModalMount) continuam sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-005 | 🟡 medium | architecture | 52.5 | Cinco páginas centrais do Wealth OS (dashboard, contas, investimentos, orçamento, portadores) continuam sem nenhum teste de página. |
| ARCH-009 | 🟡 medium | architecture | 40 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) não tem nenhuma cobertura de teste, direta ou indireta — todo consumidor testado o exercita apenas de forma incidental, sem testar o comportamento de teclado/foco em si. |
| FIN-006 | 🟠 high | finance | 30 | A fórmula de patrimônio líquido continua implementada duas vezes de forma independente (NetWorthSnapshotService e ReportsController#net_worth) em vez de uma única fonte reutilizada. |
| FIN-007 | 🟡 medium | finance | 30 | PortfolioService#allocation reporta 0.0% de alocação para todos os tipos de investimento sempre que o custo líquido total da carteira é zero ou negativo, mesmo havendo posições reais, sem nenhum teste cobrindo esse caso. |
| SEC-003 | 🟡 medium | security | 30 | apps/klipper-web segue com 4 advisories (1 low, 3 high) em devDependencies transitivas do toolchain de build (esbuild, fast-uri, js-yaml, svgo), não embarcadas no bundle de produção mas exercitadas em todo `npm run dev`/CI; desta vez bundler-audit e brakeman (apps/klipper-api) rodaram normalmente neste ambiente (rede disponível) e não encontraram nenhuma vulnerabilidade Ruby/Rails, então a lacuna de cobertura de auditorias anteriores nesse lado foi fechada. |
| FIN-008 | 🟡 medium | finance | 28.8 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o item de rastreabilidade da checklist financeira do projeto. |
| ARCH-010 | 🟡 medium | architecture | 27 | O docstring de ModalStress.test.ts afirma cobrir o fechamento de modal por ESC e clique no backdrop, mas nenhum teste do arquivo exercita esse comportamento — reforça a falsa sensação de que o dismiss por teclado (o mesmo caminho não testado em base-modal-focus-trap-untested) está coberto. |
| ARCH-007 | 🟡 medium | architecture | 26.67 | StockQuoteService — a única integração HTTP com serviço externo de toda a API (brapi.dev) — não tem spec dedicado, e os caminhos de erro/parsing seguem sem cobertura de teste. |
| ARCH-006 | 🟡 medium | architecture | 25 | ReportsController mistura dois padrões arquiteturais no mesmo arquivo: metade das actions agrega dados financeiros inline, a outra metade delega a Calculator services. |
| FIN-009 | 🟢 low | finance | 18 | ReimbursementCoverageCalculator pode reportar coverage_pct acima de 100% quando o valor reembolsado excede o gasto do mês de referência, e esse caso nunca é exercitado por teste. |
| ARCH-008 | 🟡 medium | architecture | 12 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados byte a byte entre os dois arquivos. |
| SEC-004 | 🟡 medium | security | 9 | GET /api/v1/quotes continua interpolando o parâmetro `tickers`, informado pelo usuário autenticado, sem validar contra um charset restrito antes de montar a URL de saída para brapi.dev, permitindo injetar segmentos extras de path/query e derrubando a ação com 500 para entradas malformadas. |
| SEC-005 | 🟢 low | security | 8 | PATCH /api/v1/password_resets/:token (redenção do token de reset) segue sem rate limiting, ao contrário de toda outra action de autenticação não-autenticada; o token é gerado por `generate_token_for` (valor assinado do Rails, não um código curto adivinhável), então a exploração prática é limitada — é uma lacuna de defesa em profundidade/carga de banco, não um caminho de força bruta realista hoje. |
| FIN-010 | 🟡 medium | finance | 5 | StockQuoteService, que faz parsing de dado de preço de investimento vindo de uma API externa (brapi.dev), não tem nenhuma cobertura de teste — nem caminho normal nem erro — violando a regra de calculo/dado financeiro sem teste, embora hoje não haja consumidor no frontend que exponha o resultado ao usuário. |
| FIN-005 | 🟡 medium | finance | 4.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição que o próprio autor documentou como não verificada, e nenhum teste cobre um débito real. |
| SEC-006 | 🟢 low | security | 4 | O access token JWT (15 min de validade) continua em um cookie legível por JavaScript no cliente, diferente do refresh token que é HttpOnly, e não há CSP configurada no Nuxt para reduzir o raio de um XSS futuro; isso é defesa em profundidade insuficiente ainda que nenhum sink de XSS explorável tenha sido encontrado nesta auditoria. |
