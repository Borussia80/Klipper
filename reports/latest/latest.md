# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `258607dedd6e3ad824ac53d8d257cc89ea4725cb` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | critical |
| Segurança | medium |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-002 | 🟠 high | architecture | 450 | A lógica de validação e parsing de valores financeiros de useLancamentoForm — compartilhada pelos modais de novo e editar lançamento — continua sem teste unitário dedicado. |
| FIN-001 | 🟡 medium | finance | 250 | InstrumentReadout ainda hardcoda o rótulo "% da renda" e o texto de estado nulo "Sem orçamento definido", então orcamento.vue (que mede % do orçamento alocado, não % da renda) exibe a mesma leitura textual do dashboard (que mede % da renda) — a matemática está certa, a leitura do usuário não. |
| ARCH-003 | 🟠 high | architecture | 128 | A fórmula de patrimônio líquido (contas + investimentos) continua duplicada entre NetWorthSnapshotService e ReportsController#net_worth em vez de reutilizar o service existente. |
| FIN-004 | 🟡 medium | finance | 105 | O spentRatio do hero do dashboard continua com um computed local não testado que devolve 0 em vez de null quando não há receita no ciclo, reintroduzindo a mesma ambiguidade "sem dado" vs "zero" já corrigida em orcamento.vue via budgetSpentRatio — a função correta (pctOfIncome) já existe e já está importada no mesmo arquivo, só não é usada aqui. |
| SEC-002 | 🟢 low | security | 80 | O endpoint não-autenticado /api/v1/health continua devolvendo `Rails.env` no corpo JSON, permitindo que qualquer chamador anônimo identifique se o alvo é produção/staging/desenvolvimento. |
| FIN-003 | 🔴 critical | finance | 67.5 | BankImport::AmountParser continua assumindo convenção BR (vírgula=decimal) sempre que a string contém vírgula, corrompendo silenciosamente valores en-US com milhar por vírgula e decimal por ponto (ex.: "1,234.56" vira 1.23456) sem levantar erro — usado tanto por CsvImportService quanto por todos os PdfAdapters, então o bug atinge qualquer import de extrato/fatura nesse formato. |
| ARCH-004 | 🟡 medium | architecture | 60 | Quatro componentes Vue de entrada/edição de dados financeiros (nova conta, novo membro, editar reembolso, e o wrapper ModalMount) continuam sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-005 | 🟡 medium | architecture | 52.5 | Cinco páginas centrais do Wealth OS (dashboard, contas, investimentos, orçamento, portadores) continuam sem nenhum teste de página. |
| ARCH-009 | 🟡 medium | architecture | 40 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) não tem nenhuma cobertura de teste, direta ou indireta — todo consumidor testado o exercita apenas de forma incidental, sem testar o comportamento de teclado/foco em si. |
| FIN-006 | 🟠 high | finance | 30 | A fórmula de patrimônio líquido (contas + investimentos, via Investment.signed_cost_sql) continua duplicada entre NetWorthSnapshotService e ReportsController#net_worth em vez de reutilizar um único método — exatamente o padrão de duplicação de dado patrimonial entre telas/endpoints que a checklist financeira pede para vigiar, e a mesma classe de bug que já causou FIN-002 (net-worth-snapshot-ignores-sell-sign) quando as duas implementações divergiram no sinal de venda. |
| SEC-003 | 🟡 medium | security | 30 | apps/klipper-web continua com 4 advisories (1 low, 3 high) em devDependencies transitivas do toolchain Vite/Nuxt (esbuild, fast-uri, js-yaml, svgo), nenhuma delas embarcada no bundle de produção, mas todas exercitadas em toda invocação de dev/CI; apps/quebec-web já foi corrigido para o mesmo conjunto de pacotes. |
| ARCH-010 | 🟡 medium | architecture | 27 | O docstring de ModalStress.test.ts afirma cobrir o fechamento de modal por ESC e clique no backdrop, mas nenhum teste do arquivo exercita esse comportamento — reforça a falsa sensação de que o dismiss por teclado (o mesmo caminho não testado em base-modal-focus-trap-untested) está coberto. |
| ARCH-007 | 🟡 medium | architecture | 26.67 | StockQuoteService — a única integração HTTP com serviço externo de toda a API (brapi.dev) — não tem spec dedicado, e os caminhos de erro/parsing seguem sem cobertura de teste. |
| ARCH-006 | 🟡 medium | architecture | 25 | ReportsController mistura dois padrões arquiteturais no mesmo arquivo: metade das actions agrega dados financeiros inline, a outra metade delega a Calculator services. |
| ARCH-008 | 🟡 medium | architecture | 12 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados byte a byte entre os dois arquivos. |
| SEC-004 | 🟡 medium | security | 9 | GET /api/v1/quotes interpola o parâmetro `tickers`, informado pelo usuário autenticado, sem escapar ou validar, dentro da URL de saída para brapi.dev, permitindo injetar segmentos extras de path/query e derrubando a ação com 500 (URI::InvalidURIError não tratado) para entradas malformadas (ex: espaço). |
| SEC-005 | 🟢 low | security | 8 | PATCH /api/v1/password_resets/:token (redenção do token de reset) não tem rate limiting, ao contrário de toda outra action de autenticação não-autenticada; o token é gerado por `generate_token_for` (valor assinado do Rails, não um código curto adivinhável), então a exploração prática é limitada — é uma lacuna de defesa em profundidade/carga de banco, não um caminho de força bruta realista hoje. |
| FIN-005 | 🟡 medium | finance | 4.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição explicitamente não verificada pelo próprio autor e sem nenhum teste de débito — se um extrato real usar convenção diferente para débito, o valor entraria com sinal invertido no saldo/patrimônio sem nenhum teste capaz de pegar a regressão. |
| SEC-006 | 🟢 low | security | 2.4 | O access token JWT (15 min de validade) é armazenado em um cookie legível por JavaScript no cliente, diferente do refresh token que é HttpOnly; isso é defesa em profundidade insuficiente contra roubo de token via um XSS futuro, ainda que nenhum sink de XSS explorável tenha sido encontrado nesta auditoria. |
