# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `c911320e997eec51b13ca9676b681a897a30b9f7` · **Modo:** fast

## Score geral: 48.67/100 (-14 vs baseline)

## Seções

| Seção | Score | Risco | Tendência |
|---|---|---|---|
| Arquitetura | 70 | high | +4 |
| Domínio financeiro | 6 | high | -36 |
| Segurança | 70 | high | -10 |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| SEC-004 | 🟠 high | security | 504 | quebec-web (site institucional público, sem autenticação) expõe em produção a rota `/_ipx` do @nuxt/image, que processa imagens com `sharp`/`ipx` vulneráveis a CVEs de alta severidade em libvips/libheif, mesmo sem nenhum componente do app usar o módulo — superfície de ataque presente sem nenhum benefício de produto, o inverso do que já foi feito em klipper-web. |
| FIN-001 | 🟡 medium | finance | 250 | A página de orçamento reutiliza InstrumentReadout, cujos textos fixos ("% da renda") descrevem o percentual como participação na renda, mas o valor exibido ali é participação no orçamento alocado do ciclo — o cálculo está correto, o rótulo mostrado ao usuário não é. |
| ARCH-002 | 🟠 high | architecture | 112 | A lógica de validação e parsing de valores financeiros compartilhada pelos modais de novo e editar lançamento (ModalNovoLancamento, ModalEditarLancamento) continua sem teste unitário dedicado, apesar de o próprio código documentar um bug de regressão anterior causado por essa mesma divergência silenciosa. |
| SEC-002 | 🟢 low | security | 80 | O endpoint público /api/v1/health devolve `Rails.env` no corpo JSON, permitindo que qualquer chamador anônimo identifique se o alvo é produção/staging/desenvolvimento. |
| FIN-003 | 🔴 critical | finance | 54 | BankImport::AmountParser interpreta qualquer vírgula como separador decimal brasileiro e corrompe silenciosamente valores em formato en-US (vírgula-milhar, ponto-decimal) vindos de importação de CSV genérico, sem lançar erro nem ter teste que cubra o caso — mesmo finding já catalogado (FIN-003), ainda não corrigido no código atual. |
| ARCH-007 | 🟡 medium | architecture | 40 | O caminho de erro da integração com a API externa de cotações (brapi.dev) — JSON malformado, timeout, falha de rede — está implementado no controller mas nunca é exercitado por teste algum, direto ou de request. |
| ARCH-003 | 🟡 medium | architecture | 20 | A fórmula de patrimônio líquido (contas + investimentos) continua duplicada entre NetWorthSnapshotService e ReportsController#net_worth em vez de reutilizar um método comum, embora a causa raiz do risco de inconsistência (fórmula de custo sem sinal) já tenha sido corrigida — severidade rebaixada de high para medium desde a auditoria anterior. |
| ARCH-004 | 🟡 medium | architecture | 16 | Quatro componentes Vue de entrada de dados financeiros (nova conta, novo membro, editar reembolso, e o roteador de modais ModalMount) continuam sem nenhuma cobertura de teste, direta ou indireta — o único teste que os referencia os stuba explicitamente. |
| SEC-003 | 🟡 medium | security | 15 | Ambos os apps frontend carregam devDependencies transitivas desatualizadas (esbuild, svgo, vitest, js-yaml, fast-uri) com advisories moderate/high publicados; nenhum desses pacotes específicos roda em produção, mas seguem sem patch em toda máquina de desenvolvedor e job de CI, e o gate de CI do quebec-web só corta em `--audit-level=critical`. |
| SEC-005 | 🟢 low | security | 12 | QuotesController encaminha o parâmetro `tickers` do usuário direto para dentro da URL de uma chamada HTTP externa (brapi.dev) sem validar caracteres nem limitar a quantidade de tickers, e não trata o `URI::InvalidURIError` que um ticker com caractere inválido dispara — resultando em erro 500 não tratado; uma lista muito longa gera uma única requisição externa arbitrariamente grande, sem estar sujeita a rate limiting. |
| ARCH-005 | 🟡 medium | architecture | 10 | Cinco páginas centrais do Wealth OS (dashboard, contas, investimentos, orçamento, portadores) continuam sem nenhum teste de página. |
| ARCH-006 | 🟡 medium | architecture | 6 | ReportsController continua misturando dois padrões arquiteturais no mesmo arquivo: metade das actions agrega dados financeiros inline, a outra metade delega a Calculator services — sem mudança desde a última auditoria. |
