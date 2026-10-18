# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `a4b01be086e656269eefcc6c2cc6b286da411231` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | high |
| Domínio financeiro | critical |
| Segurança | low |

## Possible Regressions

- **ARCH-013** — medium → high: apps/klipper-api/app/models/investment.rb:38-45 define signed_cost e signed_cost_sql (cobertos por teste de paridade em spec/models/investment_spec.rb:102-113), mas apps/klipper-api/app/models/investment.rb:70-78 (sufficient_quantity_for_sell) reimplementa o mesmo sinal buy/sell numa terceira forma ('i.operation_type == "sell" ? -i.quantity : i.quantity'), fora do teste de paridade.

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| FIN-011 | 🔴 critical | finance | 300 | O campo account.balance — que compõe accounts_total em TODO cálculo de patrimônio líquido do app (NetWorthSnapshotService, relatório de patrimônio, dashboard) — nunca é escrito por nenhum fluxo real: a criação de conta não pede saldo, não existe tela de edição de saldo para contas que não são cartão, e nem o import de CSV nem o de PDF (que já extrai a coluna 'saldo' do extrato em BaseAdapter::Row, mas descarta o valor) gravam esse dado; para qualquer usuário que só usa o fluxo normal do produto (criar conta → importar extrato), balance permanece 0 para sempre e o patrimônio líquido/saldo em contas exibido no app nunca reflete dinheiro real. |
| ARCH-011 | 🟡 medium | architecture | 112 | useModal (roteamento de todo modal financeiro do app, via ModalMount.vue) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — open()/close()/reset de payload e o auto-dismiss via setTimeout em useToast.ts:15 só são exercitados incidentalmente através de mocks em testes de componentes individuais. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento) exibe um rótulo semanticamente errado para a métrica que de fato calcula — mesmo finding já catalogado como FIN-001, ainda sem correção. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) não tem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-004 | 🟡 medium | architecture | 48 | ModalNovaConta ganhou cobertura desde a última auditoria, mas ModalNovoMembro, ModalEditarReembolso e o próprio ModalMount — que decide qual modal financeiro renderizar a partir do nome em useModal — continuam sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-005 | 🟡 medium | architecture | 30 | Dashboard ganhou teste de página desde a última auditoria, mas três páginas centrais do Wealth OS (contas, orçamento, portadores) continuam sem nenhum teste de página. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído — o AuditLog criado em ImportsController guarda o checksum do arquivo e a contagem, mas nenhuma transação individual referencia esse registro, quebrando o requisito de rastreabilidade da seção financeira. Mesmo finding já catalogado como FIN-008, ainda sem correção. |
| ARCH-013 | 🟠 high | architecture | 22.5 | A lógica de sinal buy/sell que já causou o bug real FIN-002 quando duplicada entre services tem agora uma terceira reimplementação (dentro da validação de venda suficiente), não coberta pelo teste de paridade signed_cost/signed_cost_sql — uma mudança futura na regra de sinal pode divergir silenciosamente ali sem que nenhum teste acuse. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. Mesmo finding já catalogado como FIN-005, ainda sem correção (risco aceito e documentado, não silenciado). |
| SEC-003 | 🟢 low | security | 10.8 | `esbuild` (low, recorrente, só no dev server) segue sem correção publicada em ambos os frontends; a varredura de dependências Ruby não pôde ser executada neste ambiente por falta de `bundle` instalado. |
| ARCH-008 | 🟢 low | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. |
| ARCH-014 | 🟢 low | architecture | 9 | O padrão visual de campo com select (label, wrapper, seta customizada) continua reimplementado em CSS scoped duplicado em pelo menos três modais de entidade diferentes dos de lançamento, então qualquer ajuste visual precisa ser replicado manualmente em cada arquivo. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer throttle no Rack::Attack, ao contrário de todas as outras rotas de autenticação não-autenticadas. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call; o caminho é inalcançável via fluxo normal do app (validação impede amount_limit <= 0), mas dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. Mesmo finding já catalogado como FIN-010, ainda sem correção. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA segue exposto a JavaScript via cookie não-httpOnly, e o ADR-2026-09-17-003 que propõe aceitar esse risco (mitigado por CSP) continua em `proposed`, sem decisão formal. |
