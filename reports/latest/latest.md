# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `92b87fef5abd2e1242a68dd5cdc298e17585aad6` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | critical |
| Segurança | low |

## Possible Regressions

- **FIN-005** — medium → critical: apps/klipper-api/app/services/pdf_adapters/btg_extrato_adapter.rb:15-19 — comentário do próprio autor: 'Confirmado apenas contra 1 relatório real com 5 lançamentos, todos RENDIMENTOS (crédito). Sem exemplo real de débito... assume-se que a coluna já usa o sinal correto'; apps/klipper-api/spec/services/pdf_adapters/btg_extrato_adapter_spec.rb só exercita casos de crédito.
- **FIN-010** — low → medium: apps/klipper-api/app/services/budget_engine.rb:16 — `pct = budget.amount_limit.positive? ? (spent / budget.amount_limit * 100).round(1) : 0.0`, travado por apps/klipper-api/spec/services/budget_engine_spec.rb:59-63 (`expect(result.first[:pct_used]).to eq(0.0)`); diverge da convenção nil usada em portfolio_service.rb:22 e reimbursement_coverage_calculator.rb:57 para o mesmo tipo de razão sem denominador válido.

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| FIN-001 | 🟡 medium | finance | 120 | InstrumentReadout continua com o rótulo hardcoded '% da renda', então orcamento.vue exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — open()/close()/reset de payload e o auto-dismiss via setTimeout só são exercitados incidentalmente através de mocks em testes de componentes individuais, enquanto os dois outros composables-singleton do mesmo padrão (useConnectionStatus, useServerWaking) já foram cobertos desde a última auditoria. |
| ARCH-004 | 🟡 medium | architecture | 72 | De quatro modais financeiros sem nenhuma cobertura identificados na auditoria anterior, dois (ModalNovaConta, ModalEditarCartao) já ganharam teste de montagem; ModalNovoMembro e ModalEditarReembolso continuam sem nenhum teste. ModalMount.vue também não tem teste, mas é só um dispatcher condicional sem lógica própria — risco residual bem menor que os outros dois. |
| ARCH-009 | 🟡 medium | architecture | 56 | O composable de focus trap compartilhado por todos os modais do app (Escape para fechar, Tab/Shift+Tab no limite da lista focável, restauração de foco ao gatilho) continua sem nenhuma cobertura de teste, direta ou indireta — sem mudança desde a última auditoria. |
| FIN-008 | 🟡 medium | finance | 42 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| FIN-005 | 🔴 critical | finance | 28 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal, violando a regra de cálculo financeiro sem cobertura de borda. |
| ARCH-005 | 🟡 medium | architecture | 24 | De quatro páginas centrais do Wealth OS sem nenhum teste de página identificadas na auditoria anterior, três (dashboard, contas, orçamento) já foram corrigidas; só portadores.vue continua sem teste de página. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell (documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada) continua com uma terceira reimplementação em sufficient_quantity_for_sell, fora do teste de paridade existente entre signed_cost e signed_cost_sql — uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que esse teste acuse. Sem mudança desde a última auditoria. |
| FIN-011 | 🔴 critical | finance | 18 | Quando o total do mês é zero ou negativo (ex.: um estorno grande superando os débitos de outras naturezas), NaturezaSplitCalculator zera o pct de TODAS as naturezas mesmo que uma delas tenha gasto real diferente de zero, repetindo sem correção a mesma classe de bug que FIN-007 já corrigiu em PortfolioService#allocation. |
| SEC-003 | 🟢 low | security | 18 | Ambos os frontends (klipper-web e quebec-web) continuam com dependências moderate/low desatualizadas — incluindo o próprio Nuxt, dependência direta de produção — que o gate de CI aceita por design (só bloqueia high/critical), então o portão fica verde sem que a dívida seja corrigida. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos — sem mudança desde a última auditoria. |
| FIN-012 | 🟡 medium | finance | 9.6 | spent, remaining e pct_used de BudgetEngine#summary não têm teste de borda para o caso de gasto líquido negativo (estorno maior que despesa na mesma categoria no mês), deixando o comportamento resultante (remaining acima do limite alocado, pct_used negativo) sem documentação nem proteção contra regressão. |
| ARCH-014 | 🟡 medium | architecture | 9 | O padrão visual de campo (label, wrapper, mensagem de erro) é reimplementado em CSS scoped duplicado em múltiplos modais de entidade fora do par de lançamento, então qualquer ajuste visual precisa ser replicado manualmente em cada arquivo e tende a divergir — sem mudança desde a última auditoria. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado — sem mudança desde a última auditoria. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token — a redenção do token de reset de senha, única rota de autenticação pública sem exigir token válido previamente — continua sem qualquer rate limiting, ao contrário de sign_in, sign_up e da criação do próprio reset. |
| FIN-010 | 🟡 medium | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em outros dois calculators financeiros para a mesma situação de denominador inválido; a validação do model impede amount_limit <= 0 no fluxo normal, mas dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| FIN-013 | 🟡 medium | finance | 3.6 | A assinatura de NetWorthSnapshotService promete 'patrimônio em at', mas a implementação sempre calcula com saldos/posições de hoje; o risco é documentado pelo próprio autor e não é acionado pelo único agendamento existente, mas uma chamada futura com data passada sobrescreveria silenciosamente um snapshot histórico com dados atuais. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA permanece exposto a JavaScript via cookie não-httpOnly (em contraste com o refresh token, que é httpOnly — apps/klipper-api/app/controllers/api/v1/auth_controller.rb:60-67), e o ADR-2026-09-17-003 que deveria formalizar essa decisão arquitetural segue em `proposed`, sem resolução. |
