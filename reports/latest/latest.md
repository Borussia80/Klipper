# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `a05ef686abcda0a016ec23fec0e165d730f142b9` · **Modo:** fast

> ⚠️ **Relatório incompleto.** A análise de **architecture** não produziu resultado neste run. O que segue abaixo cobre só 2 das 3 seções esperadas — ausência de finding numa área não avaliada não significa ausência de problema.

## Seções

| Seção | Risco |
|---|---|
| Domínio financeiro | medium |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento, não da renda) exibe um rótulo semanticamente errado para a métrica que de fato calcula — recorrência confirmada do finding já catalogado. |
| FIN-011 | 🟡 medium | finance | 30 | NaturezaSplitCalculator usa 0.0 para 'sem base de cálculo válida' em pct por natureza, a mesma ambiguidade zero-vs-nil já catalogada em BudgetEngine (FIN-010) e evitada em PortfolioService/ReimbursementCoverageCalculator (que usam nil) — mas aqui, diferente do BudgetEngine (cujo caso zero é inatingível via fluxo normal porque a validação do model impede amount_limit<=0), o caminho é alcançável em uso real: a feature de estorno/reembolso (Lacuna 4) pode legitimamente lançar um crédito de estorno num mês sem despesa nova equivalente na mesma natureza, zerando ou negativando o total do mês e fazendo o donut do dashboard mostrar '0%' para todas as naturezas em vez de sinalizar base inválida. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF continua sem poder ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído — o AuditLog adicionado por SEC-20 registra que um import aconteceu, mas não liga cada transação individual a esse registro, então o requisito de rastreabilidade da seção financeira continua quebrado. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. |
| SEC-003 | 🟢 low | security | 10.8 | Dependências de desenvolvimento/transitivas de ambos os frontends seguem com advisories moderate/low abertas (atualmente `esbuild` e a cadeia de `minimatch` via eslint/typescript-eslint); o lado Ruby não pôde ser auditado nesta execução por falta de `bundle`/gems instaladas no ambiente. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é coberto por teste e inalcançável via fluxo normal do app (validação impede amount_limit <= 0), mas dado legado ou uma edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural de aceitar esse risco (mitigado pela CSP com nonce) ou migrar para cookie HttpOnly + CSRF segue sem resolução formal. |
