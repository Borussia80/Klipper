# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `ff9220814c4b7254f77bca8e76d41092b7054e72` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | medium |
| Segurança | medium |

## Possible Regressions

- **SEC-003** — low → medium: apps/klipper-web/package-lock.json e apps/quebec-web/package-lock.json resolvem nuxt@3.21.11 em ambos; `npm audit --json` rodado localmente em ambos reporta 11 advisories high + 1 low na árvore transitiva do nuxt, dependências marcadas dev:false no lockfile (ou seja, na árvore 'de produção' do npm, não em devDependencies): braces (GHSA-vfj7-8cjw-p6xm, stack-exhaustion DoS, <=3.0.3, via micromatch->fast-glob/globby) e node-forge (GHSA-86w9-cpqp-85rv, bypass de verificação de assinatura RSA PKCS#1 v1.5, <=1.4.0, via listhen->nitropack->@nuxt/cli, usado para gerar certificado HTTPS do dev server). `fixAvailable` para ambos exige bump de major (nuxt@4.6.2). Isso é uma escalada em relação à última auditoria (SEC-003, 2026-09-18), que só encontrava devalue (moderate, já resolvido — devalue@5.9.4 não aparece mais no audit) e esbuild (low, ainda presente). Evidence unavailable quanto à exposição real em produção: braces/micromatch/fast-glob/globby/listhen/nitropack são ferramentas de build/CLI/dev-server do Nuxt, e não foi possível confirmar nesta auditoria (sem acesso ao output buildado da Vercel) se algum desses módulos é de fato carregado pela function serverless em runtime de produção, ou se ficam restritos ao pipeline de build.

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 243 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — open()/close()/reset de payload e o auto-dismiss via setTimeout só são exercitados incidentalmente através de mocks em testes de componentes individuais. |
| ARCH-009 | 🟡 medium | architecture | 106.67 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) não tem nenhuma cobertura de teste, direta ou indireta. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento) exibe um rótulo semanticamente errado para a métrica que de fato calcula — o número está certo, o rótulo mente sobre o que ele mede. |
| ARCH-004 | 🟡 medium | architecture | 50 | Três componentes Vue de entrada/edição de dados financeiros (ModalNovoMembro, ModalEditarReembolso, ModalMount) continuam sem nenhuma cobertura de teste, direta ou indireta, embora ModalNovaConta já tenha sido corrigido desde a última auditoria. |
| ARCH-005 | 🟡 medium | architecture | 50 | Três páginas centrais do Wealth OS (contas, orçamento, portadores) continuam sem nenhum teste de página, embora dashboard já tenha sido corrigido desde a última auditoria. |
| ARCH-013 | 🟡 medium | architecture | 36 | A lógica de sinal buy/sell (documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada) tem uma terceira reimplementação em sufficient_quantity_for_sell, não coberta pelo teste de paridade existente entre signed_cost e signed_cost_sql, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste de paridade acuse. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído (mesmo com a trilha de auditoria agregada de SEC-20), quebrando o requisito de rastreabilidade da seção financeira no nível de linha. |
| ARCH-014 | 🟡 medium | architecture | 20 | O padrão visual de campo com select (label, wrapper, seta customizada) é reimplementado em CSS scoped duplicado em pelo menos cinco modais de entidade diferentes, então qualquer ajuste visual (ex: acessibilidade do caret, espaçamento) precisa ser replicado manualmente em cada arquivo e tende a divergir. |
| SEC-003 | 🟡 medium | security | 20 | klipper-web e quebec-web compartilham a mesma árvore de dependências do nuxt@3.21.11, que agora carrega 11 advisories de severidade high (destaque para bypass de verificação de assinatura RSA no node-forge e DoS por stack-exhaustion no braces) resolvíveis só por upgrade de major para nuxt@4; a superfície de exploração real em produção não pôde ser confirmada porque os pacotes afetados pertencem ao toolchain de build/dev-server, não ao código de request-handling. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal (débito viraria crédito e vice-versa) caso a suposição esteja errada. |
| ARCH-008 | 🟡 medium | architecture | 12 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. |
| ARCH-015 | 🟢 low | architecture | 12 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| ARCH-016 | 🟢 low | architecture | 12 | ImportsController#create e #confirm duplicam verbatim a lógica de derivar o status do audit log (success/failure) a partir de result.imported/duplicates/errors, em vez de centralizar num método privado único. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem nenhuma regra de throttle no Rack::Attack, ao contrário das demais rotas de autenticação não-autenticadas. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é coberto por teste e inalcançável via fluxo normal do app (validação impede amount_limit <= 0), mas dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly (`klipper_token`), e a decisão arquitetural registrada em ADR-2026-09-17-003 (aceitar o risco mitigado por CSP, ou migrar para cookie HttpOnly + CSRF) segue sem resolução formal. |
