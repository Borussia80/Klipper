# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `b0468204fa20236860ce1d01f1e1805eb2a421b1` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | medium |
| Segurança | medium |

## Possible Regressions

- **ARCH-009** — medium → high: apps/klipper-web/components/ui/__tests__/BaseModal.test.ts agora existe (novo desde a última auditoria), mas suas duas únicas specs ('mostra a ação do rodapé fora da área rolável' e 'não cria rodapé quando o formulário não tem ação fixa') cobrem só o slot de rodapé fixo — nenhuma menção a Escape/Tab/focus em todo o arquivo (grep vazio), e não existe composables/__tests__/useFocusTrap.test.ts.

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — open()/close()/reset de payload e o auto-dismiss via setTimeout só são exercitados incidentalmente através de mocks em testes de componentes individuais. |
| ARCH-016 | 🟠 high | architecture | 93.33 | TransfersController — a única rota que move dinheiro entre duas contas do usuário (debit+credit) — não tem nenhum request spec, enquanto todo outro controller da API tem um; os códigos de status (201/404/422), o rescue de TransferService::InvalidTransfer e o parâmetro de contas escopado a current_user só são verificados hoje por leitura de código, nunca por teste de integração. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento) exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| ARCH-009 | 🟠 high | architecture | 56 | O componente-base compartilhado por todos os modais do app ganhou um arquivo de teste desde a última auditoria, mas ele cobre apenas o layout do rodapé — o focus trap em si (Escape para fechar, Tab/Shift+Tab circulando entre os elementos focáveis, restauração de foco ao gatilho ao fechar) permanece sem nenhuma cobertura, direta ou indireta. |
| ARCH-004 | 🟡 medium | architecture | 33.33 | Um dos quatro componentes Vue de entrada/edição de dados financeiros apontados na última auditoria (ModalNovaConta) já ganhou cobertura de montagem; ModalNovoMembro, ModalEditarReembolso e ModalMount continuam sem nenhum teste, direto ou indireto. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| SEC-001 | 🟡 medium | security | 24 | apps/quebec-web roda com `ssr: true` em Nuxt 3.21.11, versão afetada por CVEs moderados de divulgação da mensagem/dados de erros não tratados durante SSR e de bypass de route rules via barra codificada em rotas catch-all, sem uma página de erro customizada que contenha o vazamento — a mesma classe de risco da ocorrência anterior (SEC-001), reaberta por advisories publicados depois daquela correção. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell (documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada) tem uma terceira reimplementação não coberta pelo teste de paridade existente entre signed_cost e signed_cost_sql, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste de paridade acuse. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. |
| ARCH-014 | 🟢 low | architecture | 12 | O padrão visual de campo com select (label, wrapper, seta customizada) continua reimplementado em CSS scoped duplicado, agora observável em pelo menos cinco modais de entidade diferentes (um a mais que na última auditoria), então qualquer ajuste visual precisa ser replicado manualmente em cada arquivo e tende a divergir. |
| SEC-003 | 🟢 low | security | 12 | Dependências de build/dev (não o `nuxt` em si, tratado separadamente para apps/quebec-web) seguem desatualizadas em devDependencies transitivas de ambos os frontends; nesta execução foi possível, pela primeira vez, instalar o bundler compatível e confirmar que o lado Ruby de apps/klipper-api está livre de CVEs conhecidos. |
| ARCH-008 | 🟢 low | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. |
| ARCH-005 | 🟢 low | architecture | 8 | Três das quatro páginas centrais do Wealth OS apontadas na última auditoria (dashboard, contas, orçamento) já ganharam teste de página; só portadores continua sem nenhum. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; o caminho é coberto por teste e inalcançável via fluxo normal do app (validação impede amount_limit <= 0), mas dado legado ou uma edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural de aceitar esse risco (mitigado pela CSP com nonce) ou migrar para cookie HttpOnly + CSRF segue sem resolução formal. |
