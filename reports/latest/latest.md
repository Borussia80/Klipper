# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `77c3e640cfd2d5905ef3f613f0fa3077b26da146` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | critical |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto; ambos só são tocados por mocks em testes de outros componentes. |
| ARCH-009 | 🟡 medium | architecture | 70 | O fechamento por Escape e por clique no backdrop do componente-base compartilhado por todos os modais do app continua sem nenhuma cobertura; a parte de focus trap (useFocusTrap) melhorou e agora é exercitada indiretamente via CommandPalette.test.ts, mas o comportamento próprio de BaseModal (Escape/backdrop) segue descoberto. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento) exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| ARCH-005 | 🟡 medium | architecture | 33.33 | Das quatro páginas centrais do Wealth OS sem teste na auditoria anterior (dashboard, contas, orçamento, portadores), dashboard e orçamento já ganharam teste de página; contas e portadores continuam sem nenhum. |
| ARCH-004 | 🟡 medium | architecture | 33.33 | Dos quatro componentes de entrada/edição de dados financeiros sem cobertura na auditoria anterior, ModalNovaConta já ganhou teste; ModalNovoMembro, ModalEditarReembolso e o próprio ModalMount (o roteador de modais) continuam sem nenhuma cobertura. |
| FIN-011 | 🔴 critical | finance | 30 | NaturezaSplitCalculator reporta 0,0% para todas as naturezas quando o total do mês é negativo (estornos de uma natureza superando o gasto), apagando o percentual de uma natureza que de fato teve gasto real — o mesmo padrão de bug já corrigido em PortfolioService#allocation (FIN-007), só que aqui o `0.0` continua indistinguível de "sem base para calcular". |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell tem uma terceira reimplementação em sufficient_quantity_for_sell, não coberta pelo teste de paridade existente entre signed_cost e signed_cost_sql — uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste acuse. |
| SEC-003 | 🟢 low | security | 20 | `esbuild`/`braces`/`node-forge` continuam desatualizados em devDependencies transitivas de ambos os frontends sem versão corrigida publicada (já mitigado por exceção explícita no CI gate), e o lado Ruby segue impossível de verificar neste sandbox por falta de bundler instalável. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. |
| ARCH-014 | 🟡 medium | architecture | 15 | O padrão visual de campo com select (label, wrapper, seta customizada) continua reimplementado em CSS scoped duplicado — e a duplicação se espalhou de 3 para 5 arquivos desde a última auditoria, agora incluindo DataHealthBanner.vue, que não é um modal de entidade. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o <style scoped> inteiro continuam duplicados quase byte a byte entre os dois arquivos. |
| SEC-005 | 🟢 low | security | 7.5 | PATCH /api/v1/password_resets/:token (confirmação da nova senha com o token de reset) continua sem rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é coberto por teste e inalcançável via fluxo normal do app (validação impede amount_limit <= 0), mas dado legado ou uma edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 4 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural correspondente (ADR-2026-09-17-003) segue em `proposed/` sem ter sido formalmente aceita ou substituída. |
