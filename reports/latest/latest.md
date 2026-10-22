# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `e30543bc38934869b077ff2e91f3521d99982276` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | medium |
| Segurança | low |

## Possible Regressions

- **ARCH-009** — medium → high: apps/klipper-web/components/ui/BaseModal.vue (164 linhas) e composables/useFocusTrap.ts (39 linhas) — nenhum arquivo components/ui/__tests__/BaseModal.test.ts ou composables/__tests__/useFocusTrap.test.ts existe no checkout.
- **ARCH-004** — medium → high: apps/klipper-web/components/ui/ModalNovoMembro.vue, ModalEditarReembolso.vue e ModalMount.vue ainda não têm arquivo correspondente em components/ui/__tests__/. ModalNovaConta.vue, que estava na mesma lista na última auditoria, já tem components/ui/__tests__/ModalNovaConta.test.ts — a lista encolheu de 4 para 3 componentes.

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-016 | 🟠 high | architecture | 400 | O middleware global que decide, para toda navegação do SPA, se o usuário é redirecionado para /login, autenticado via refresh, ou liberado para a rota pedida, não tem nenhum teste — justo na mesma PR que reformulou o fluxo de sessão (login explícito após cadastro/redefinição de senha) e tornou esse redirecionamento mais crítico. |
| ARCH-017 | 🟠 high | architecture | 360 | login.vue — o único ponto de entrada de autenticação do app e a página que acabou de absorver a lógica de cadastro sem login automático — não tem nenhum teste de página, enquanto as duas páginas vizinhas do mesmo fluxo (esqueci-senha, redefinir-senha) já seguem o padrão de teste do projeto. |
| ARCH-009 | 🟠 high | architecture | 189 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap em useFocusTrap.ts e restauração de foco ao gatilho) continua sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-004 | 🟠 high | architecture | 147 | Três componentes Vue de entrada/edição de dados financeiros (ModalNovoMembro, ModalEditarReembolso, ModalMount) continuam sem nenhuma cobertura de teste; ModalNovaConta, antes na mesma lista, já foi corrigido. |
| ARCH-011 | 🟠 high | architecture | 144 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — open()/close()/reset de payload e o auto-dismiss via setTimeout só são exercitados incidentalmente através de mocks em testes de componentes individuais. |
| ARCH-005 | 🟡 medium | architecture | 90 | Da lista original de quatro páginas centrais do Wealth OS sem teste (dashboard, contas, orçamento, portadores), dashboard e orçamento já foram corrigidos; contas e portadores continuam sem nenhum teste de página. |
| ARCH-013 | 🟡 medium | architecture | 63 | A lógica de sinal buy/sell (documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada) tem uma terceira reimplementação em sufficient_quantity_for_sell não coberta pelo teste de paridade existente entre signed_cost e signed_cost_sql, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste de paridade acuse. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded no template, então orcamento.vue (que mede % do orçamento gasto) e contas.vue exibem um rótulo semanticamente errado para a métrica que de fato calculam. |
| FIN-008 | 🟡 medium | finance | 40 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| ARCH-008 | 🟡 medium | architecture | 26.67 | ModalNovoLancamento e ModalEditarLancamento continuam compartilhando a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. |
| ARCH-014 | 🟢 low | architecture | 20 | O padrão visual de campo com select (label, wrapper, seta customizada) é reimplementado em CSS scoped duplicado em pelo menos cinco modais de entidade diferentes, então qualquer ajuste visual (ex: acessibilidade do caret, espaçamento) precisa ser replicado manualmente em cada arquivo e tende a divergir. |
| ARCH-015 | 🟢 low | architecture | 18 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| FIN-005 | 🟡 medium | finance | 8 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste exercita esse caminho — um extrato real com débito na conta corrente pode importar o valor com sinal invertido silenciosamente. |
| SEC-003 | 🟢 low | security | 8 | esbuild segue desatualizado como devDependency transitiva de ambos os frontends, expondo um low-severity de leitura arbitrária de arquivo no dev server (Windows-only); fica abaixo do limiar high/critical que .github/scripts/audit-gate.mjs bloqueia, então o CI não falha por causa disso. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é inalcançável via fluxo normal do app (validação impede amount_limit <= 0 na criação de budget), mas dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural de aceitar esse risco ou migrar para cookie HttpOnly + CSRF segue sem resolução formal (ADR ainda proposed). |
