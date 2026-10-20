# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `e16b90e134cd11985b23b14161035f80629b7078` · **Modo:** fast

> ⚠️ **Relatório incompleto.** As análises de **architecture**, **finance** não produziram resultado neste run. O que segue abaixo cobre só 1 das 3 seções esperadas — ausência de finding numa área não avaliada não significa ausência de problema.

## Seções

| Seção | Risco |
|---|---|
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| SEC-003 | 🟢 low | security | 18 | As duas únicas advisories 'high' presentes no npm audit de ambos os frontends (braces ReDoS e node-forge RSA signature bypass) seguem sem versão corrigida publicada pelo Nuxt, mas já estão cobertas por exceção explícita e justificada no portão de CI (audit-gate.mjs), com o restante (vite/esbuild moderate/low) já catalogado em SEC-003; nenhuma advisory nova sem tratamento foi encontrada nesta auditoria. |
| SEC-005 | 🟢 low | security | 6 | O endpoint de redenção de token de reset de senha continua sem rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas, permitindo tentativas ilimitadas de adivinhar um token válido por IP. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-HttpOnly, e a decisão arquitetural de aceitar ou mitigar esse risco segue sem resolução formal. |
