# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `cdc7b60f7e3b679afbb0f44ab189b494eccbbfd7` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | medium |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal e useToast — os dois composables singleton que controlam todo o roteamento de modal e todo o feedback ao usuário no app — continuam sem nenhum teste direto de open/close/reset/auto-dismiss. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded no template, então orcamento.vue (que mede gasto sobre limite de orçamento) exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape, focus trap, restauração de foco) continua sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-004 | 🟡 medium | architecture | 33.33 | 3 dos 4 componentes de entrada/edição financeira antes sem cobertura continuam sem nenhum teste (ModalNovoMembro, ModalEditarReembolso, ModalMount); ModalNovaConta foi corrigido desde a última auditoria — melhora parcial. |
| ARCH-005 | 🟡 medium | architecture | 33.33 | 2 das 4 páginas centrais do Wealth OS antes sem teste continuam sem cobertura (contas, portadores), ambas com fluxo de confirmação de exclusão (contas.vue:129-138, portadores.vue:92-101) não exercitado; dashboard e orçamento foram corrigidas desde a última auditoria — melhora parcial. |
| ARCH-016 | 🟡 medium | architecture | 30 | A regra D1 (gasto líquido = débito regular menos estorno) é reimplementada independentemente em 5 calculators diferentes, sem helper ou scope compartilhado — o mesmo padrão de risco que já causou divergência real na fórmula de signed_cost (FIN-002/ARCH-003). |
| SEC-006 | 🟢 low | security | 30 | O access token da SPA segue exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural de aceitar esse risco (mitigado por CSP) ou migrar para cookie HttpOnly + CSRF continua sem resolução formal (ADR ainda em `proposed/`). |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell, já documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada, tem uma terceira reimplementação (posição líquida para validar venda) fora do teste de paridade existente. |
| SEC-005 | 🟢 low | security | 18 | O endpoint de redenção de token de reset de senha (PATCH /api/v1/password_resets/:token) continua sem qualquer rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas. |
| ARCH-017 | 🟡 medium | architecture | 16 | ReportsController#net_worth reimplementa inline a quebra de custo por investment_type que PortfolioService#allocation já calcula, com formato diferente (sem pct_of_portfolio) — a mesma inconsistência de padrão que motivou ARCH-006 persiste nesta action específica, que ficou fora do escopo da correção. |
| FIN-010 | 🟢 low | finance | 12 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é coberto por teste e inalcançável via fluxo normal do app (validação de Budget provavelmente impede amount_limit <= 0), mas dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| FIN-005 | 🟡 medium | finance | 12 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. |
| FIN-008 | 🟢 low | finance | 11.25 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento continuam com template de apresentação e CSS scoped inteiro duplicados quase byte a byte, apesar da lógica já estar centralizada em useLancamentoForm. |
| ARCH-014 | 🟡 medium | architecture | 9 | O padrão visual de campo com select e o banner de erro de formulário são reimplementados em CSS scoped duplicado em pelo menos 5 e 10 modais de entidade respectivamente, exigindo replicação manual a cada ajuste visual. |
| ARCH-018 | 🟢 low | architecture | 9 | ModalNovoAporte.vue reimplementa inline a validação e montagem de payload que, para lançamentos, já foi extraída para useLancamentoForm.ts — o padrão de extração não foi replicado para o fluxo de investimentos. |
| SEC-003 | 🟢 low | security | 8 | esbuild transitivo (via vite/nuxt) segue na faixa vulnerável a leitura arbitrária de arquivo no dev server (Windows-only, severidade low) em ambos os frontends, sem versão corrigida ainda absorvida pelo lockfile. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' continua duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar do diretório de concerns já existir no projeto para esse propósito. |
