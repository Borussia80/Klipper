# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `1f12484d6e13976083764e6eeb671350d0566bae` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | medium |
| Segurança | low |

## Possible Regressions

- **SEC-006** — low → medium: apps/klipper-web/composables/useApi.ts:18-22 — o access token da SPA é guardado em `useCookie<string | null>('klipper_token', { sameSite: 'lax', secure: cookieSecure, maxAge: 60 * 15 })`, sem `httpOnly` (que o Nuxt não pode setar do lado cliente de qualquer forma). O refresh token, por contraste, já é httpOnly (apps/klipper-api/app/controllers/api/v1/auth_controller.rb:59-66).
- **SEC-005** — low → medium: apps/klipper-api/config/initializers/rack_attack.rb:3-5 — o throttle `auth/ip` só casa path exato contra `%w[/api/v1/auth/sign_in /api/v1/auth/sign_up /api/v1/password_resets]`; a rota de redenção `PATCH /api/v1/password_resets/:token` (config/routes.rb:10) nunca aparece nessa lista porque o path inclui o token. Nenhum outro throttle do arquivo cobre `PasswordResetsController#update` (apps/klipper-api/app/controllers/api/v1/password_resets_controller.rb:16-27).

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — open()/close()/reset de payload e o auto-dismiss via setTimeout só são exercitados incidentalmente através de mocks em testes de componentes individuais. Sem mudança desde a última auditoria. |
| ARCH-004 | 🟡 medium | architecture | 60 | Quatro componentes Vue de entrada/edição de dados financeiros continuam sem nenhuma cobertura de teste, direta ou indireta. Sem mudança desde a última auditoria. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout ainda exibe o sufixo fixo '% da renda' mesmo quando a razão renderizada mede % do orçamento (orcamento.vue), continuando a divergência semântica já catalogada. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) não tem nenhuma cobertura de teste, direta ou indireta. Sem mudança desde a última auditoria — o gap inclusive foi documentado de forma explícita no docstring de outro arquivo de teste (correção do finding ARCH-010), mas a lacuna em si não foi fechada. |
| SEC-006 | 🟡 medium | security | 36 | O access token JWT (15 min de validade) continua acessível a qualquer script no contexto da página via `document.cookie`/`useCookie`, então um XSS bem-sucedido em qualquer ponto da SPA exfiltra o token diretamente, sem precisar driblar `httpOnly`. |
| ARCH-005 | 🟡 medium | architecture | 33.33 | Três páginas centrais do Wealth OS (contas, orçamento, portadores) continuam sem nenhum teste de página. Melhora parcial em relação à última auditoria: dashboard.vue ganhou pages/__tests__/dashboard.test.ts, amarrado à correção do bug FIN-004 (spentRatio tratando ausência de receita como 0% gasto) — não sobrou nenhuma página sem teste apenas por acidente, o padrão de 'adicionar teste junto da correção do bug' está sendo seguido. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| SEC-003 | 🟢 low | security | 30 | Dependências transitivas/de build (`devalue`, `esbuild`) seguem desatualizadas em klipper-web e quebec-web com advisories publicadas — nenhuma delas afeta código de produção server-side, mas ambas têm correção disponível via atualização. |
| SEC-007 | 🟢 low | security | 30 | A SPA define uma CSP com nonce bem construída (`frame-ancestors 'none'` já cobre clickjacking), mas não define explicitamente `Strict-Transport-Security`, `Referrer-Policy`, `X-Content-Type-Options` nem `Permissions-Policy` — não há evidência no código de que a Vercel injete esses headers por padrão para este projeto, então a confirmação de que eles chegam ao navegador depende de configuração da plataforma fora do checkout (Evidence unavailable para o comportamento em runtime). |
| SEC-005 | 🟡 medium | security | 24 | O endpoint que consome o token de redefinição de senha (PATCH /api/v1/password_resets/:token) segue sem qualquer rate limit, ao contrário do endpoint de criação do pedido de reset, que é o único coberto pelo throttle `auth/ip`. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell (documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada) tem uma terceira reimplementação não coberta pelo teste de paridade existente entre signed_cost e signed_cost_sql, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste de paridade acuse. Sem mudança desde a última auditoria. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição não verificada contra nenhum débito real, e nenhum teste trava esse sinal, deixando risco de inversão silenciosa em dados de patrimônio de importações BTG. |
| ARCH-016 | 🟢 low | architecture | 18 | A verificação de senha atual antes de operações sensíveis (excluir conta, trocar e-mail, trocar senha) está reimplementada três vezes com o mesmo corpo em vez de um único before_action/método privado parametrizado. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. Sem mudança desde a última auditoria. |
| ARCH-014 | 🟡 medium | architecture | 9 | O padrão visual de campo com select (label, wrapper, seta customizada) é reimplementado em CSS scoped duplicado em pelo menos três modais de entidade diferentes dos de lançamento, então qualquer ajuste visual (ex: acessibilidade do caret, espaçamento) precisa ser replicado manualmente em cada arquivo e tende a divergir. Sem mudança desde a última auditoria. |
| ARCH-017 | 🟢 low | architecture | 8 | A lógica de derivar total e status de auditoria (success/failure) a partir de um ImportResult está duplicada entre os actions create e confirm de ImportsController em vez de viver como método no próprio result ou como helper privado único. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. Sem mudança desde a última auditoria. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil adotada em outros dois calculators para o mesmo tipo de razão sem denominador válido; caminho inalcançável via fluxo normal do app (validação impede amount_limit <= 0), mas dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
