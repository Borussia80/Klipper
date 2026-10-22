# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `c3a38ef0b6081c866ea0b63e22954812ac85f330` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | high |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 252 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — mesma situação da auditoria anterior, sem progresso. |
| ARCH-009 | 🟡 medium | architecture | 202.5 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) continua sem nenhuma cobertura de teste — o gap já é reconhecido explicitamente no código, mas ainda não foi fechado. |
| ARCH-013 | 🟡 medium | architecture | 72 | A lógica de sinal buy/sell, já documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada, tem uma terceira reimplementação na validação de venda que pode divergir silenciosamente sem que o teste de paridade existente acuse. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento, não da renda) exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| FIN-011 | 🟠 high | finance | 56 | O detector de transferência-própria (OwnTransferMatcher) foi mesclado e é bem testado no backend, mas sua sugestão nunca chega à UI de importação de PDF nem é usada para marcar a transação como kind: "transfer"; na prática, toda transferência entre contas próprias importada via PDF continua sendo contada como despesa na conta de origem e receita na conta de destino, inflando total_debits/total_credits (dashboard, relatório mensal, orçamento) exatamente no cenário que a feature deveria evitar. |
| ARCH-004 | 🟡 medium | architecture | 48 | Dos quatro componentes de entrada/edição financeira sem cobertura apontados na auditoria anterior, ModalNovaConta foi corrigido; ModalNovoMembro, ModalEditarReembolso e ModalMount continuam sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-005 | 🟡 medium | architecture | 48 | Das quatro páginas centrais do Wealth OS sem teste apontadas na auditoria anterior, dashboard foi corrigida; contas, orçamento e portadores continuam sem nenhum teste de página. |
| ARCH-008 | 🟡 medium | architecture | 32 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o <style scoped> inteiro continuam duplicados byte a byte entre os dois arquivos — sem progresso desde a auditoria anterior. |
| ARCH-014 | 🟡 medium | architecture | 30 | O padrão visual de campo com select (label, wrapper, seta customizada) continua reimplementado em CSS scoped idêntico em três modais de entidade diferentes dos de lançamento — sem progresso desde a auditoria anterior. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| ARCH-006 | 🟢 low | architecture | 27 | A extração de agregação inline para Calculator services (ADR-2026-09-16-001) cobriu #monthly e #natureza_split, mas a action #net_worth do mesmo controller ainda monta `investments_by_type` com agregação inline, reproduzindo em escala menor a mesma inconsistência de padrão já identificada nesse controller. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. |
| ARCH-015 | 🟢 low | architecture | 18 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito — sem progresso desde a auditoria anterior. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token continua sem rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é coberto por teste e inalcançável via fluxo normal do app (validação impede amount_limit <= 0), mas dado legado ou uma edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-003 | 🟢 low | security | 4 | esbuild (transitivo, usado pelo dev server do Vite/Nuxt) continua numa faixa com advisory low sem fix publicado em ambos os frontends; o restante do antigo achado (devalue) já foi corrigido. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA segue exposto a JavaScript via cookie não-httpOnly, com a decisão arquitetural correspondente (ADR-2026-09-17-003) ainda sem resolução formal. |
