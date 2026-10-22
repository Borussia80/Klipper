# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `be3536a7c706fbf04339ea96809e70eee6c28bdf` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | high |
| Domínio financeiro | medium |
| Segurança | low |

## Possible Regressions

- **ARCH-004** — medium → high: ModalNovaConta.vue ganhou teste direto (components/ui/__tests__/ModalNovaConta.test.ts, 2 casos) desde a última auditoria, mas ModalNovoMembro.vue (109 linhas), ModalEditarReembolso.vue (100 linhas) e ModalMount.vue (51 linhas) continuam sem arquivo .test.ts correspondente em components/ui/__tests__/ — grep por 'ModalNovoMembro'/'ModalEditarReembolso'/'ModalMount' em *.test.ts só retorna menções em comentários ou stubs (layouts/__tests__/app.test.ts:48 declara UiModalMount como stub raso), nunca uma montagem real do componente.
- **ARCH-013** — medium → critical: apps/klipper-api/app/models/investment.rb:70-78 — Investment#sufficient_quantity_for_sell soma posição com `i.operation_type == "sell" ? -i.quantity : i.quantity`, uma terceira reimplementação do sinal buy/sell já existente como #signed_cost e .signed_cost_sql (linhas 38-46). spec/models/investment_spec.rb:102-113 só testa paridade entre signed_cost e signed_cost_sql; sufficient_quantity_for_sell não entra nesse teste de paridade (bundle exec rspec confirma 738 examples / 0 failures sem cobrir esse caso, portanto a suíte passa mesmo que esse terceiro cálculo divirja).

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-009 | 🟡 medium | architecture | 126 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco) continua sem nenhuma cobertura de teste direta, apenas exercitado incidentalmente via mocks em testes de modais individuais. |
| ARCH-011 | 🟡 medium | architecture | 90 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário), ambos com estado singleton module-level, continuam sem nenhum teste direto de open/close, reset de payload ou auto-dismiss via setTimeout. |
| ARCH-004 | 🟠 high | architecture | 70 | Três componentes de entrada/edição de dados financeiros (membro, reembolso, e o roteador de modais ModalMount) continuam com zero cobertura de teste direta ou indireta, embora ModalNovaConta — citado no mesmo finding anterior — já tenha sido corrigido. |
| ARCH-005 | 🟡 medium | architecture | 60 | Três páginas centrais do Wealth OS (contas, orçamento, portadores) continuam sem nenhum teste de página, embora dashboard já tenha sido corrigido desde a última auditoria. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento) exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| ARCH-013 | 🔴 critical | architecture | 54 | A regra de sinal buy/sell tem uma terceira implementação independente em sufficient_quantity_for_sell, não coberta pelo teste de paridade signed_cost/signed_cost_sql — é cálculo financeiro (posição de investimento) sem teste cobrindo a mesma classe de divergência silenciosa que já causou o incidente financeiro real documentado no próprio arquivo (FIN-002), então por padrão do contrato compartilhado trato como critical. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| FIN-011 | 🟡 medium | finance | 20 | Quando o total agregado por natureza do mês é zero ou negativo (ex.: estorno de uma natureza supera o débito do mês), NaturezaSplitCalculator#by_natureza zera o pct de todas as naturezas, inclusive as que têm gasto real positivo, escondendo a distribuição real no gráfico em vez de sinalizar 'sem dado' como já é feito em PortfolioService#allocation (pct: nil) para o mesmo tipo de razão sem base válida. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal da coluna 'Movimentação R$' sem inversão, mas essa suposição nunca foi validada contra um débito real nem é travada por teste, deixando dado de patrimônio de importações BTG com risco não coberto de inversão silenciosa de sinal. |
| ARCH-008 | 🟡 medium | architecture | 16 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. |
| ARCH-014 | 🟢 low | architecture | 9 | O padrão visual de campo com select (label, wrapper, seta customizada) é reimplementado em CSS scoped quase idêntico em pelo menos três modais de entidade além dos de lançamento, então qualquer ajuste visual precisa ser replicado manualmente em cada arquivo. |
| ARCH-015 | 🟢 low | architecture | 8 | A regra 'occurred_on não pode ser futuro' permanece duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar do diretório de concerns já existir no projeto para esse propósito. |
| SEC-003 | 🟢 low | security | 8 | O esbuild low (sem versão corrigida publicada) segue como a única pendência residual real da cadeia de dependências de front-end; braces/node-forge têm exceção formal revisada e devalue saiu de cena com o bump de versão, e agora o lado Ruby também está confirmado limpo via bundler-audit/brakeman nesta execução. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas — permite tentativas ilimitadas de adivinhar um token de reset válido. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é coberto por teste e inalcançável via fluxo normal do app (validação impede amount_limit <= 0), mas dado legado ou uma edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural de aceitar esse risco (mitigado pela CSP com nonce) ou migrar para cookie HttpOnly + CSRF segue sem resolução formal — o ADR permanece em `proposed`. |
