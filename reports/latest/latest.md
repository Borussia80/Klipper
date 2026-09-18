# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `1f0de6efe919549d38b6833d8627f1cb54834235` · **Modo:** fast

> ⚠️ **Relatório incompleto.** A análise de **finance** não produziu resultado neste run. O que segue abaixo cobre só 2 das 3 seções esperadas — ausência de finding numa área não avaliada não significa ausência de problema.

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Segurança | low |

## Possible Regressions

- **SEC-003** — low → medium: npm audit (apps/klipper-web/package-lock.json): devalue <5.9.1 — GHSA-9rgm-9g3h-6x36, DoS via input malformado, severity moderate, CVSS 5.3; esbuild 0.27.3-0.28.0 — GHSA-g7r4-m6w7-qqqr, leitura arbitrária de arquivo no dev server em Windows, severity low. apps/quebec-web: mesma advisory de esbuild (low), devalue não aparece na árvore desta vez. bin/bundler-audit rodou nesta execução (ambiente com Ruby 3.3.12 + bundle install bem-sucedido) e não encontrou vulnerabilidades no lado Rails — a lacuna de verificação do lado Ruby registrada nas últimas auditorias está resolvida.

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | Sem mudança desde a última auditoria: useModal (roteamento de todo modal financeiro, incluindo o novo fluxo de importação) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto. |
| ARCH-009 | 🟡 medium | architecture | 56 | Sem mudança desde a última auditoria: o componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) continua sem nenhuma cobertura de teste, direta ou indireta. |
| ARCH-005 | 🟡 medium | architecture | 33.33 | Melhorou parcialmente: dashboard.vue ganhou teste de página desde a última auditoria (eram 4 páginas sem cobertura, agora restam 3 — contas, orçamento e portadores). |
| ARCH-004 | 🟡 medium | architecture | 30 | Melhorou parcialmente: de quatro componentes de entrada/edição financeira sem cobertura, dois foram corrigidos (ModalNovaConta, ModalNovoAporte); restam ModalEditarReembolso e ModalNovoMembro. |
| ARCH-014 | 🟡 medium | architecture | 30 | Piorou desde a última auditoria: o padrão visual de campo com select continua reimplementado em CSS scoped duplicado, e a feature mais recente (importar.vue, DataHealthBanner.vue) adicionou duas novas cópias em vez de reaproveitar uma existente — a superfície de duplicação cresceu de pelo menos 3 para 8 arquivos. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | Sem mudança desde a última auditoria: a regra de sinal buy/sell — causa documentada do bug real FIN-002 quando duplicada — tem uma terceira reimplementação (validação de venda) não coberta pelo teste de paridade existente entre signed_cost e signed_cost_sql. |
| SEC-003 | 🟡 medium | security | 18 | devalue (moderate, DoS) e esbuild (low, leitura de arquivo em dev server Windows) seguem desatualizados em devDependencies transitivas dos dois frontends Nuxt; o gate de CI (`npm audit --audit-level=high`) não bloqueia porque ambas ficam abaixo do limiar high. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | Sem mudança desde a última auditoria: ModalNovoLancamento e ModalEditarLancamento compartilham a lógica via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados byte a byte. |
| ARCH-015 | 🟢 low | architecture | 6 | Sem mudança desde a última auditoria: a regra 'occurred_on não pode ser futuro' segue duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token continua sem rate limiting, permitindo tentativas ilimitadas de adivinhar um token de reset válido por IP. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA segue exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural sobre aceitar esse risco residual ou migrar o fluxo de auth continua sem resolução formal. |
