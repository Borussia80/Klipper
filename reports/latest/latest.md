# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `644a62796a47d658235e256ff45903d31ea12ccf` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | high |
| Segurança | low |

## Possible Regressions

- **SEC-003** — low → medium: npm audit (2026-10-30) em apps/klipper-web e apps/quebec-web: nuxt@3.21.11 (resolvido a partir do range ^3.15.4 em ambos os package.json) está na faixa vulnerável de três advisories — GHSA-vjh5-4x84-xrqp (route rules ignoradas em paths com variação de maiúsculas/minúsculas, moderate), GHSA-xfq5-w38q-pc2x (useHeadSafe de server islands sem sanitização, moderate, CVSS 5.4), GHSA-jjm6-p2m9-9w4x (javascript: URL em NuxtLink, low) — e o fix exige nuxt@4.6.3 (bump de major). seroval (moderate, só em klipper-web, via node_modules/seroval) e esbuild/nitropack/workbox-build/@rollup-plugin-node-resolve/deepmerge (low, ambos os apps) seguem desatualizados nas duas lockfiles. `grep -rn 'NuxtIsland\|componentIsland'` e `grep -rn routeRules` em apps/klipper-web e apps/quebec-web não encontraram nenhum uso de server islands nem de routeRules, o que reduz a exploitabilidade real das duas advisories moderate mais graves — mas o código vulnerável segue presente em produção.

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — a lacuna é a mesma identificada na auditoria anterior, sem progresso. |
| ARCH-004 | 🟡 medium | architecture | 60 | Dos quatro componentes de entrada/edição de dados financeiros sem cobertura identificados na auditoria anterior, um (ModalNovaConta) foi corrigido; ModalNovoMembro, ModalEditarReembolso e ModalMount continuam com zero cobertura de teste, direta ou indireta. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento alocado) exibe um rótulo semanticamente errado para a métrica que de fato calcula — finding já catalogado, segue sem correção. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) continua sem nenhuma cobertura de teste — a própria suíte que antes alegava cobrir isso (ARCH-010, já resolvido) hoje documenta corretamente a lacuna, mas a lacuna em si persiste. |
| FIN-011 | 🔴 critical | finance | 48 | Em MonthlySummaryCalculator#by_category e em NaturezaSplitCalculator#totals, um estorno (kind "refund") cuja categoria/natureza não teve despesa no mesmo mês nunca é deduzido da fatia correspondente, fazendo a soma do detalhamento por categoria/natureza divergir do total do mês mostrado no mesmo dashboard — e esse caso de borda não tem nenhum teste cobrindo-o, violação direta da regra de cálculo financeiro sem teste. |
| ARCH-005 | 🟡 medium | architecture | 40 | Das quatro páginas centrais do Wealth OS sem teste identificadas na auditoria anterior, duas (dashboard, orçamento) foram corrigidas; contas, portadores e o detalhe de conta (contas/[id]) continuam sem nenhum teste de página. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell, que o próprio código documenta como causa do bug real FIN-002 quando duplicada, continua com uma terceira reimplementação fora do teste de paridade existente, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste de paridade acuse. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. |
| ARCH-014 | 🟡 medium | architecture | 15 | O padrão visual de campo com select (classe fi-sel, wrapper e seta customizada) agora está reimplementado em CSS scoped duplicado em cinco arquivos diferentes (quatro modais de entidade e um banner), não mais só três — a duplicação não foi endereçada e ganhou mais um ponto de divergência. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos — sem alteração desde a última auditoria. |
| SEC-003 | 🟡 medium | security | 9 | Ambos os frontends Nuxt (klipper-web e quebec-web) têm nuxt pinado em ^3.15.4, uma faixa sem patch disponível para três CVEs conhecidas (duas moderate, uma low) cujo fix exige upgrade de major para a linha 4.x, além de dependências transitivas (seroval, esbuild, nitropack) desatualizadas. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' continua duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em outros dois calculators para o mesmo tipo de razão sem denominador válido; dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural de aceitar esse risco (mitigado pela CSP com nonce em apps/klipper-web/server/middleware/csp.ts) ou migrar para cookie HttpOnly + CSRF segue sem resolução formal. |
