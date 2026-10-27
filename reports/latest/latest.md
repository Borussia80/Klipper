# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `842c4f6dfec8618b23cd2843d4bc173f763b290f` · **Modo:** fast

> ⚠️ **Relatório incompleto.** A análise de **architecture** não produziu resultado neste run. O que segue abaixo cobre só 2 das 3 seções esperadas — ausência de finding numa área não avaliada não significa ausência de problema.

## Seções

| Seção | Risco |
|---|---|
| Domínio financeiro | medium |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout tem o rótulo fixo '% da renda' hardcoded no template, então orcamento.vue (que mede proporção do orçamento gasto, não renda) exibe um rótulo semanticamente errado para a métrica que de fato calcula — a matemática está certa, a leitura é ambígua. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade do domínio financeiro. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal caso a suposição esteja errada. |
| SEC-003 | 🟢 low | security | 18 | Ambos os frontends (klipper-web e quebec-web) carregam nuxt 3.21.11 com 3 advisories moderate e 1 low que o portão de CI (audit-gate.mjs, só bloqueia high/critical) nunca vai pegar, e as condições de exploração (routeRules, server islands, pages desabilitado) não estão presentes no código hoje, mas o código vulnerável continua embarcado. |
| SEC-007 | 🟢 low | security | 12 | O caminho de decode-failure do JWT (token malformado, assinatura inválida, expirado) é testado isoladamente em JwtService mas nunca exercitado via request spec contra uma rota protegida real, deixando o comportamento fim-a-fim do portão de autenticação sem cobertura direta para esse cenário específico. |
| SEC-005 | 🟢 low | security | 6 | O endpoint PATCH /api/v1/password_resets/:token (redenção do token de reset) continua fora de qualquer regra de throttle do Rack::Attack, permitindo tentativas ilimitadas de adivinhar/forçar um token de reset por IP. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada por dois outros calculadores de proporção financeira do mesmo domínio; o caminho é inalcançável via fluxo normal do app (validação de Budget impede amount_limit <= 0), mas dado legado ou edição direta no banco ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural (ADR-2026-09-17-003) de aceitar formalmente esse risco ou migrar para httpOnly+CSRF segue sem resolução. |
