# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `f6eb451acb547bded2e2f2a3b6ee23b4929a2889` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | medium |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto desde a última auditoria — open()/close()/reset de payload e o auto-dismiss via setTimeout em useToast só são exercitados incidentalmente através de mocks (mockNuxtImport) em testes de componentes individuais, nunca a lógica do composable isolada. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento gasto, não da renda) exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) continua sem nenhuma cobertura de teste, direta ou indireta. |
| SEC-005 | 🟢 low | security | 48 | O endpoint que consome o token de redefinição de senha (PATCH /api/v1/password_resets/:token) não está sob nenhum rate limit, permitindo força bruta do token sem bloqueio por IP ou por conta. |
| ARCH-004 | 🟡 medium | architecture | 40 | Dos quatro componentes antes catalogados sem cobertura, ModalNovaConta foi corrigido desde a última auditoria. ModalNovoMembro e ModalEditarReembolso — que têm validação e submissão próprias, não só template — continuam sem nenhuma cobertura de teste, direta ou indireta. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF continua sem nenhuma referência persistida ao lote/arquivo de origem (a trilha de auditoria SEC-20 registra o evento de importação em si, não liga cada transação de volta a ele), então não é possível, a partir de uma transação em transacoes.vue, provar de qual importação ela veio. |
| ARCH-014 | 🟡 medium | architecture | 28 | O padrão visual de campo select com seta customizada é reimplementado em CSS scoped duplicado em pelo menos 7 componentes usando duas convenções de nome diferentes (select-wrap/select-arrow vs. sel-wrap/sel-caret), e a duplicação já produziu uma divergência real: o valor de centralização vertical do caret (translateY) ficou diferente entre arquivos que deveriam renderizar o mesmo visual — confirmando o risco já registrado na auditoria anterior de que o padrão tende a divergir quando replicado manualmente. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell — documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada — continua com uma terceira reimplementação em sufficient_quantity_for_sell que não é coberta pelo teste de paridade existente entre signed_cost e signed_cost_sql, então uma mudança futura na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste de paridade acuse. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal caso um débito real use formatação diferente da assumida. |
| ARCH-005 | 🟡 medium | architecture | 18 | Das quatro páginas centrais do Wealth OS antes catalogadas sem teste, dashboard e orçamento foram corrigidas desde a última auditoria (investimentos já havia sido corrigido antes). contas.vue e portadores.vue continuam sem nenhum teste de página. |
| FIN-011 | 🟢 low | finance | 13.5 | O chip de cobertura do dashboard mistura a razão do mês corrente com um alerta calculado sobre janelas acumuladas de meses, sem distinguir as duas escalas — exatamente o bug já descrito em ROADMAP_KLIPPER_WEALTH_OS.md ('dashboard.vue — chip de alerta acumulado colado no número mensal') com critério de aceite registrado mas ainda não implementado no código atual. |
| SEC-006 | 🟢 low | security | 12 | O access token de 15 minutos fica em um cookie legível por JavaScript (não HttpOnly), então um XSS no SPA consegue roubar o token diretamente, diferente do refresh token que é HttpOnly (apps/klipper-api/app/controllers/api/v1/auth_controller.rb:60-67). |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o bloco <style scoped> inteiro continua duplicado byte a byte entre os dois arquivos (147 de 161 linhas idênticas), e boa parte do template de apresentação (campos de valor, categoria, conta, status, data) também se repete. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| SEC-003 | 🟢 low | security | 4.8 | Ambos os apps Nuxt do monorepo ficam presos na linha 3.21.x do Nuxt, que carrega um advisory moderate de bypass de route-rules e algumas deps de build com CVEs low; nenhuma é crítica/alta e a maioria afeta só o dev server/build, não o runtime servido. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; inalcançável no fluxo normal (validação de Budget impede amount_limit <= 0), mas dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
