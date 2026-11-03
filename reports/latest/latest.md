# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `5f0744020f1701b3d5337845a64a19452b11fc5a` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | medium |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — mesmo estado da auditoria anterior. |
| ARCH-004 | 🟡 medium | architecture | 75 | Três dos quatro componentes de entrada/edição financeira antes sinalizados continuam sem cobertura de teste; ModalNovaConta foi corrigido desde a última auditoria, mas ModalNovoMembro, ModalEditarReembolso e ModalMount permanecem descobertos. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então a página de orçamento (que mede proporção do orçamento, não da renda) exibe um rótulo semanticamente incorreto para a métrica que realmente calcula. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape, focus trap, restauração de foco) continua sem nenhuma cobertura de teste — mesmo estado da auditoria anterior. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell continua triplicada em investment.rb (signed_cost, signed_cost_sql, e a soma inline em sufficient_quantity_for_sell), e o teste de paridade existente não cobre a terceira forma — sem mudança desde a última auditoria. |
| ARCH-005 | 🟡 medium | architecture | 18 | Das quatro páginas centrais antes sinalizadas sem teste, três (dashboard, contas, orçamento) foram corrigidas desde a última auditoria; só portadores.vue continua sem teste de página. |
| SEC-003 | 🟢 low | security | 18 | `esbuild` (low, recorrente) segue desatualizado em devDependencies transitivas de ambos os frontends; `devalue` já foi resolvido. O toolchain de lint (ESLint/TypeScript-ESLint) acumulou uma cauda grande de avisos moderate sem fix direto, todos em devDependencies — risco real para produção é baixo, mas o `npm audit --audit-level=high` do CI (`.github/scripts/audit-gate.mjs`) não cobre essa faixa de propósito. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento continuam compartilhando template e CSS scoped quase byte a byte, sem extração para um componente de apresentação comum — sem mudança desde a última auditoria. |
| ARCH-014 | 🟡 medium | architecture | 9 | O padrão visual de campo com select continua reimplementado em CSS scoped duplicado entre modais de entidade — sem mudança desde a última auditoria. |
| SEC-007 | 🟢 low | security | 8 | `nuxt` (dependência direta, não dev) está na faixa vulnerável de uma advisory moderate de XSS via server islands, sem fix disponível fora de um salto de versão major (3.21→4.6), e isso afeta igualmente klipper-web (app com JWT e dados financeiros) e quebec-web (landing institucional). |
| SEC-008 | 🟢 low | security | 8 | O parâmetro `own_cpf_mask` (máscara de CPF do titular, usada para casar transferências próprias em importações bancárias) não está na lista de `filter_parameters`, então fica exposto em texto puro nos logs de produção a cada atualização de perfil que o envie. |
| ARCH-015 | 🟢 low | architecture | 6 | A validação 'occurred_on não pode ser futuro' continua duplicada verbatim entre Transaction e Investment em vez de um concern compartilhado — sem mudança desde a última auditoria. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem throttle, permitindo força-bruta contra o token de 30 minutos sem limite de tentativas por IP. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural de aceitar esse risco (mitigado pela CSP com nonce) ou migrar para cookie HttpOnly segue sem resolução formal no ADR. |
