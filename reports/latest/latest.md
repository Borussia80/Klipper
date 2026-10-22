# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `e626064944b273e15d53ee92757870d801519df5` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | medium |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟡 medium | architecture | 90 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — open()/close(), reset de payload entre chamadas e o auto-dismiss via setTimeout não são verificados isoladamente. |
| ARCH-009 | 🟡 medium | architecture | 80 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) e o composable useFocusTrap que o implementa continuam sem nenhuma cobertura de teste direta. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout continua com o rótulo fixo '% da renda' hardcoded, então orcamento.vue (que mede proporção do orçamento) exibe um rótulo semanticamente errado para a métrica que de fato calcula. |
| ARCH-004 | 🟡 medium | architecture | 40 | Dois componentes Vue de entrada/edição de dados financeiros (ModalEditarReembolso, ModalNovoMembro) continuam sem nenhuma cobertura de teste, direta ou indireta — escopo reduzido de quatro para dois desde a última auditoria, mas ainda não fechado. |
| ARCH-005 | 🟡 medium | architecture | 32 | Três páginas centrais do Wealth OS (contas, orçamento, portadores) continuam sem nenhum teste de página; dashboard já foi corrigido nesta mesma janela (ganhou dashboard.test.ts junto com a correção do bug FIN-004), reduzindo o escopo de quatro para três páginas. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| ARCH-013 | 🟡 medium | architecture | 24 | A regra de sinal buy/sell — já causa documentada do bug real FIN-002 quando duplicada — tem uma terceira implementação independente na validação de venda, fora do alcance do teste de paridade existente entre as outras duas formas. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. |
| ARCH-014 | 🟢 low | architecture | 18 | O padrão visual de campo `<select>` (aparência customizada, seta, padding) é reimplementado em CSS scoped duplicado em pelo menos três modais de entidade diferentes dos de lançamento, e um quarto (ModalNovaCategoria) usa a classe sem declará-la, dependendo de ordem de montagem para herdar o estilo. |
| ARCH-015 | 🟢 low | architecture | 18 | A regra 'occurred_on não pode ser futuro' continua duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o projeto já ter um diretório de concerns para esse propósito. |
| SEC-003 | 🟢 low | security | 18 | `devalue` (moderate, DoS) e `esbuild` (low, path traversal em dev server) seguem desatualizados em devDependencies transitivas de ambos os frontends; o lado Ruby não pôde ser verificado neste ambiente por falta de bundler/brakeman executáveis. |
| ARCH-008 | 🟡 medium | architecture | 15 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas continuam duplicando por completo o template de apresentação e o CSS scoped, então qualquer ajuste visual precisa ser replicado manualmente nos dois arquivos. |
| ARCH-016 | 🟡 medium | architecture | 6 | pages/onboarding.vue ficou órfã (sem nenhum link/redirect que leve a ela) desde que FirstSteps.vue assumiu o papel de onboarding no dashboard nesta mesma feature, mas o fluxo antigo continua no bundle, acessível por URL direta, com sua própria lógica de criação de conta/categoria/orçamento duplicando o que FirstSteps aciona via modais — dois caminhos de onboarding coexistindo sem que nenhum dos dois substitua o outro no código. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService#allocation e ReimbursementCoverageCalculator#call para o mesmo tipo de razão sem denominador válido; dado legado ou edição direta na base ainda produziria um card de orçamento mostrando '0% usado' em vez de sinalizar ausência de limite. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly, e o ADR que decidiria aceitar esse risco (mitigado pela CSP com nonce) ou migrar para cookie HttpOnly + CSRF segue sem resolução formal. |
