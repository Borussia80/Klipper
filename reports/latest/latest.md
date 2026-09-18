# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `82b0166686fcc050455b2794d98e3d12be56874e` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | high |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| FIN-004 | 🔴 critical | finance | 432 | O hero do dashboard ainda devolve 0 (em vez de null) quando não há receita no ciclo, então UiInstrumentReadout (components/ui/InstrumentReadout.vue:20-21) desenha a barra 'dentro da faixa' preenchida em 0% como gasto medido, e não como ausência de dado. |
| ARCH-011 | 🟠 high | architecture | 135 | useModal (roteamento de todo modal financeiro do app, incluindo o registro de qual modal está ativo e seu payload) e useToast (auto-dismiss via setTimeout de todo feedback ao usuário) continuam sendo singletons globais sem nenhum teste direto — só são exercitados incidentalmente através de mocks nos testes de componentes individuais. |
| ARCH-005 | 🟡 medium | architecture | 60 | Quatro páginas centrais do Wealth OS (dashboard, contas, orcamento, portadores) continuam sem nenhum teste de página — melhora em relação à auditoria anterior, que apontava cinco, já que investimentos.vue ganhou investimentos.test.ts nesse intervalo. |
| ARCH-004 | 🟡 medium | architecture | 60 | Quatro componentes Vue de entrada/edição de dados financeiros continuam sem nenhuma cobertura de teste, direta ou indireta, incluindo o próprio componente que decide qual modal renderizar. |
| FIN-001 | 🟡 medium | finance | 36 | InstrumentReadout continua com o rótulo fixo '% da renda' e o estado nulo genérico hardcoded no componente, então orcamento.vue exibe um rótulo semanticamente errado para a métrica que realmente calcula (% do orçamento, não % da renda). |
| ARCH-009 | 🟡 medium | architecture | 32 | O componente-base compartilhado por todos os modais do app (Escape para fechar, focus trap e restauração de foco ao gatilho) segue sem nenhuma cobertura de teste — condição agora auto-documentada no próprio código de teste, o que reduz o risco de falsa segurança mas não resolve a lacuna. |
| ARCH-013 | 🟡 medium | architecture | 30 | A lógica de sinal buy/sell — documentada no próprio arquivo como causa do bug real FIN-002 quando duplicada — tem uma terceira reimplementação não coberta pelo teste de paridade existente, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda sem que o teste acuse. |
| ARCH-014 | 🟡 medium | architecture | 20 | O padrão visual de campo com select (label, wrapper, seta customizada) continua reimplementado em CSS scoped duplicado em pelo menos três modais de entidade diferentes dos de lançamento, então qualquer ajuste visual precisa ser replicado manualmente em cada arquivo. |
| SEC-003 | 🟢 low | security | 18 | O devalue moderate (novo desde a ultima leitura, que so tinha o esbuild low) e o esbuild low seguem sem correcao em apps/klipper-web e/ou apps/quebec-web; nao confirmei se o caminho de parsing malformado do devalue e de fato alcancavel por input de usuario no Nitro do klipper-web em producao (Evidence unavailable para essa reachability especifica), so que a dependencia vulneravel esta presente na arvore de producao. |
| FIN-008 | 🟡 medium | finance | 15 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade do domínio financeiro. |
| FIN-005 | 🟡 medium | finance | 14 | BtgExtratoAdapter propaga o sinal de 'Movimentação R$' sem inversão sob uma suposição que o próprio autor documenta como não verificada contra nenhum débito real, e nenhum teste trava esse sinal — dado de patrimônio de importações BTG segue com risco não coberto de inversão silenciosa de sinal. |
| ARCH-008 | 🟡 medium | architecture | 12 | ModalNovoLancamento e ModalEditarLancamento compartilham a lógica de formulário via useLancamentoForm, mas o template de apresentação e o CSS scoped inteiro continuam duplicados quase byte a byte entre os dois arquivos. |
| ARCH-015 | 🟢 low | architecture | 12 | A regra 'occurred_on não pode ser futuro' está duplicada verbatim entre Transaction e Investment em vez de viver num concern compartilhado, apesar de o diretório de concerns já existir no projeto para esse propósito. |
| SEC-005 | 🟢 low | security | 12 | PATCH /api/v1/password_resets/:token (redencao do token de reset de senha) continua sem qualquer rate limiting, ao contrario de sign_in, sign_up e da criacao do pedido de reset. O risco pratico e atenuado porque o token vem de `generates_token_for(:password_reset, expires_in: 30.minutes)` (app/models/user.rb:4), um token assinado de alta entropia, entao forca bruta contra o token em si nao e viavel mesmo sem throttle — o gap e de defesa em profundidade (ASVS V2.2.1), nao de token adivinhavel. |
| ARCH-016 | 🟢 low | architecture | 6 | A resolução de year/month a partir de params continua duplicada verbatim em três das seis actions de ReportsController, sobrevivendo à extração de MonthlySummaryCalculator/NaturezaSplitCalculator que unificou o resto do controller — a própria ADR que fez essa extração já documenta o item como pendente sem resolvê-lo. |
| SEC-006 | 🟢 low | security | 2 | O access token JWT (validade de 15 min) segue em cookie legivel por JavaScript sem httpOnly; nenhum sink de XSS exploravel foi encontrado nesta auditoria e a CSP com nonce por request reduz bastante o raio de um XSS futuro, mas a decisao formalizada no ADR proposto para essa exposicao residual segue sem ser tomada. |
