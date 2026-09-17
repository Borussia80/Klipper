# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `71280c995f7f937b232e28f82f8771828264e5ab` · **Modo:** fast

## Score geral: 70.33/100 (+41.33 vs baseline)

## Seções

| Seção | Score | Risco | Tendência |
|---|---|---|---|
| Arquitetura | 78 | medium | +6 |
| Domínio financeiro | 55 | critical | +48 |
| Segurança | 78 | medium | +70 |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| FIN-001 | 🟡 medium | finance | 250 | InstrumentReadout continua hardcodando o texto "% da renda" e "Sem orçamento definido" em vez de recebê-los como prop, então o mesmo componente exibe leitura incorreta em orcamento.vue (mostra "% da renda" para uma razão que é, na verdade, % do orçamento alocado) — a matemática está certa, a leitura do usuário não. |
| ARCH-002 | 🟠 high | architecture | 112 | A lógica de validação e parsing de valores financeiros de useLancamentoForm — compartilhada pelos modais de novo e editar lançamento — continua sem teste unitário dedicado; apenas as funções primitivas que ela consome (isFutureDate, parseBRLAmount) são testadas em outro arquivo. |
| FIN-004 | 🟡 medium | finance | 105 | O spentRatio do hero do dashboard usa um cálculo local que devolve 0 em vez de null quando não há receita no ciclo, reintroduzindo a mesma ambiguidade "sem dado" vs "zero" que já foi corrigida em orcamento.vue via budgetSpentRatio — só que numa implementação paralela e não testada. |
| SEC-002 | 🟢 low | security | 80 | O endpoint não-autenticado /api/v1/health continua devolvendo `Rails.env` no corpo JSON, permitindo que qualquer chamador anônimo identifique se o alvo é produção/staging/desenvolvimento. |
| FIN-003 | 🔴 critical | finance | 67.5 | BankImport::AmountParser assume formato BR (vírgula = decimal) sempre que a string contém vírgula, corrompendo silenciosamente valores en-US com milhar por vírgula e decimal por ponto (ex: "1,234.56" vira 1.23456) — nenhum erro é levantado e nenhum teste cobre esse caso de borda, violando a regra de ouro de que parsing financeiro sem teste de borda não entra. |
| ARCH-009 | 🟡 medium | architecture | 64 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) não tem nenhuma cobertura de teste, direta ou indireta — todo consumidor testado o stuba em vez de exercitá-lo. |
| ARCH-007 | 🟡 medium | architecture | 40 | StockQuoteService — a única integração HTTP com serviço externo de toda a API (brapi.dev) — não tem spec dedicado, e os caminhos de erro/parsing seguem sem cobertura de teste. |
| ARCH-003 | 🟠 high | architecture | 30 | A fórmula de patrimônio líquido (contas + investimentos) continua duplicada entre NetWorthSnapshotService e ReportsController#net_worth em vez de reutilizar o service existente. |
| SEC-003 | 🟡 medium | security | 30 | apps/klipper-web ainda carrega devDependencies transitivas desatualizadas (esbuild, fast-uri, js-yaml, svgo) com advisories públicos de severidade alta/baixa, executadas em toda invocação do toolchain Vite/Nuxt em dev/CI, embora nenhuma delas entre no bundle de produção; apps/quebec-web já teve o lockfile atualizado e ficou só com o advisory low de esbuild. |
| ARCH-008 | 🟡 medium | architecture | 24 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados byte a byte entre os dois arquivos. |
| ARCH-004 | 🟡 medium | architecture | 16 | Quatro componentes Vue de entrada/edição de dados financeiros (nova conta, novo membro, editar reembolso, e o wrapper ModalMount) continuam sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-005 | 🟡 medium | architecture | 10 | Cinco páginas centrais do Wealth OS (dashboard, contas, investimentos, orçamento, portadores) continuam sem nenhum teste de página. |
| SEC-004 | 🟡 medium | security | 9 | GET /api/v1/quotes interpola o parâmetro `tickers`, informado pelo usuário autenticado, sem escapar ou validar, dentro da URL de uma chamada de saída para a API pública brapi.dev, permitindo injeção de segmentos de path/query extras e derrubando a ação com 500 (URI::InvalidURIError) para entradas malformadas (ex: espaço). |
| ARCH-006 | 🟡 medium | architecture | 6 | ReportsController mistura dois padrões arquiteturais no mesmo arquivo: metade das actions agrega dados financeiros inline, a outra metade delega a Calculator services. |
| SEC-005 | 🟢 low | security | 4.8 | PasswordResetsController#update (redenção do token de reset) não tem rate limiting, ao contrário de toda outra action de autenticação não-autenticada; exploração prática é limitada porque o token é gerado por `generates_token_for` (valor assinado do Rails, não um código curto adivinhável), então isso é uma lacuna de defesa em profundidade/carga de banco, não um caminho de força bruta realista hoje. |
| FIN-005 | 🟡 medium | finance | 1.4 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição explicitamente não verificada pelo próprio autor do código e sem nenhum teste de débito — se um extrato real usar convenção diferente para débito, o valor entraria com sinal invertido no saldo/patrimônio sem qualquer teste capaz de pegar a regressão. |
