# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `dfa98f16ade42397d3695dcf32ed4ba30dfbf367` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | high |
| Segurança | medium |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro do app) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — open()/close()/reset de payload e o auto-dismiss via setTimeout só são exercitados incidentalmente através de mocks em testes de componentes individuais. |
| FIN-011 | 🔴 critical | finance | 93.33 | A subtração de estorno (débito líquido = despesas − estornos), replicada em três calculators financeiros distintos, não é exercitada por nenhum teste — nem o caso normal (estorno parcial) nem a borda em que estornos superam despesas e o total líquido vira zero/negativo, que em NaturezaSplitCalculator força pct: 0.0 para a natureza inteira (mesmo padrão já corrigido como nil em PortfolioService#allocation). |
| FIN-012 | 🔴 critical | finance | 72 | Editar uma transferência existente (TransferService.update) não reaplica a validação de valor positivo nem de contas distintas/ativas que #create exige, permitindo gravar amount zero ou negativo nas duas pernas do ledger sem erro e sem teste que cubra esse caminho. |
| ARCH-009 | 🟡 medium | architecture | 56 | BaseModal.vue, o componente-base compartilhado por todos os modais do app, já ganhou um teste de montagem desde a última auditoria, mas ele cobre apenas o layout do rodapé — o focus trap (Escape para fechar, Tab/Shift+Tab nos extremos, restauração de foco ao gatilho) continua sem nenhuma cobertura. |
| FIN-013 | 🟡 medium | finance | 40 | A inversão de sinal da fatura Itaú está documentada para dois sentidos (compra vira débito, estorno impresso negativo vira crédito positivo), mas nenhum teste exercita o segundo caminho — um estorno real na fatura pode inverter errado sem que o spec detecte. |
| ARCH-004 | 🟡 medium | architecture | 33.33 | Três componentes Vue de entrada/edição de dados financeiros (ModalEditarReembolso, ModalMount, ModalNovoMembro) continuam sem nenhuma cobertura de teste, direta ou indireta; ModalNovaConta, o quarto componente originalmente citado, já foi corrigido. |
| SEC-007 | 🟡 medium | security | 25 | Os dois frontends (klipper-web e quebec-web) seguem pinados em nuxt@3.21.11, versão atingida por quatro advisories moderate/low novas desde a última auditoria, incluindo um vetor de XSS em server islands e um bypass de route rules por path case-variant; por serem moderate/low, passam pelo portão de CI (.github/scripts/audit-gate.mjs, que só bloqueia high/critical) sem alarme. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | A lógica de sinal buy/sell — documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada — tem uma terceira reimplementação em sufficient_quantity_for_sell não coberta pelo teste de paridade existente entre signed_cost e signed_cost_sql, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste de paridade acuse. |
| ARCH-014 | 🟡 medium | architecture | 15 | O padrão visual de campo com select (label, wrapper, seta customizada) está reimplementado como CSS scoped duplicado em pelo menos 6 modais, e já divergiu em duas convenções de nome diferentes (.sel-wrap/.sel-caret vs .select-wrap/.select-arrow) para o mesmo componente visual, então qualquer ajuste (ex: acessibilidade do caret) precisa ser replicado manualmente em cada arquivo com o nome de classe correto. |
| ARCH-005 | 🟢 low | architecture | 13.5 | Das quatro páginas centrais do Wealth OS citadas na auditoria anterior (dashboard, contas, orçamento, portadores), três já ganharam teste desde então — dashboard com cobertura ampla, contas e orçamento com um teste de regressão pontual cada — restando só portadores sem nenhum teste de página. |
| SEC-005 | 🟢 low | security | 12 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas, permitindo força bruta do token de 32+ bytes sem limite de tentativas por IP. |
| SEC-003 | 🟢 low | security | 10 | Dependências transitivas de build/lint de ambos os frontends continuam acumulando CVEs moderate/low (esbuild recorrente + 5 advisories novas) por a linha nuxt/vite não ser atualizada; como são moderate/low, o portão de CI (que só bloqueia high/critical) não apita. O lado Ruby, agora verificado nesta auditoria, está limpo. |
| SEC-006 | 🟢 low | security | 10 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural de aceitar esse risco (mitigado pela CSP com nonce) ou migrar para cookie HttpOnly + CSRF segue sem resolução formal — o ADR correspondente ainda está em `proposed`. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm e seus templates já divergiram em funcionalidades legítimas (descarte de rascunho, transferência), mas o <style scoped> inteiro continua quase byte a byte duplicado entre os dois arquivos. |
| ARCH-015 | 🟢 low | architecture | 6 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto (hoje vazio) para esse propósito. |
