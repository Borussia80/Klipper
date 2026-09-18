# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `1e73b8a2f3f85e984fddee854fca3d0469cffc5e` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | high |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| FIN-004 | 🔴 critical | finance | 576 | O hero do dashboard (UiInstrumentReadout) continua calculando spentRatio inline com fallback para 0 em vez de pctOfIncome(), então um ciclo sem receita nenhuma é desenhado como '0% gasto, dentro da faixa do ciclo' em vez de 'Sem orçamento definido' — o mesmo defeito já catalogado como FIN-004 permanece sem correção após 6 execuções de auditoria consecutivas (primeira detecção 2026-09-17, última 2026-09-18), apesar de a correção ser uma substituição de uma linha por uma função já disponível no mesmo arquivo. |
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto, cobertos só incidentalmente via mocks em testes de componente. |
| ARCH-004 | 🟡 medium | architecture | 60 | Quatro componentes Vue de entrada/edição de dados financeiros continuam sem nenhuma cobertura de teste, direta ou indireta. |
| FIN-001 | 🟢 low | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento) exibe um rótulo semanticamente errado para a métrica que de fato calcula — idêntico ao já catalogado em FIN-001. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) continua sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-005 | 🟡 medium | architecture | 45 | Quatro páginas centrais do Wealth OS (dashboard, contas, orçamento, portadores) continuam sem nenhum teste de página. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV ou PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira — continua idêntico ao estado já catalogado em FIN-008. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell, que o próprio código documenta como causa do bug real FIN-002 quando duplicada, tem uma terceira reimplementação não coberta pelo teste de paridade existente. |
| SEC-003 | 🟢 low | security | 18 | devalue e esbuild seguem desatualizados como dependências transitivas de dev em ambos os frontends Nuxt, e o lado Rails não pôde ser auditado neste ambiente por falta de bundler instalado. |
| FIN-005 | 🟡 medium | finance | 11.2 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal, idêntico ao já catalogado em FIN-005. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. |
| ARCH-014 | 🟡 medium | architecture | 9 | O padrão visual de campo com select é reimplementado em CSS scoped duplicado em pelo menos três modais de entidade diferentes dos de lançamento, então qualquer ajuste visual precisa ser replicado manualmente em cada arquivo. |
| FIN-011 | 🟡 medium | finance | 9 | Investment#gain_loss e #current_value ignoram o sinal de venda que o próprio #signed_cost da mesma classe já resolve (o fix do FIN-002): para uma posição com operation_type: sell, os dois métodos usam o custo bruto da linha em vez do custo líquido com sinal, então o dia em que StockQuoteService (que já existe e já busca current_price via brapi.dev) for conectado a eles, qualquer posição com histórico de venda vai reportar ganho/perda com sinal errado — o mesmo padrão de bug que já causou o FIN-002 no snapshot de patrimônio, latente aqui porque os métodos nunca chegaram a ser chamados nem testados. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, ao contrário das outras rotas de autenticação não-autenticadas. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é coberto por teste e inalcançável via fluxo normal do app (validação de Budget impede amount_limit <= 0), mas dado legado ou uma edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA segue exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural de aceitar esse risco ou migrar para cookie HttpOnly + CSRF (ADR-2026-09-17-003) segue sem resolução formal. |
