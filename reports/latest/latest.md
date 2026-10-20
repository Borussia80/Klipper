# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `c648bffc84bbaa957df38ebb58be4a1cd48f65e6` · **Modo:** fast

> ⚠️ **Relatório incompleto.** A análise de **architecture** não produziu resultado neste run. O que segue abaixo cobre só 2 das 3 seções esperadas — ausência de finding numa área não avaliada não significa ausência de problema.

## Seções

| Seção | Risco |
|---|---|
| Domínio financeiro | high |
| Segurança | low |

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| FIN-011 | 🔴 critical | finance | 196 | ItauFaturaAdapter inverte o sinal de toda linha da fatura para separar compra de pagamento/estorno, mas só o braço 'compra' desse cálculo tem teste — o braço 'pagamento' (que ocorre em toda fatura real) nunca é exercitado, apesar do adapter irmão (Nubank) provar que o caso é testável sem fixture real. |
| FIN-001 | 🟡 medium | finance | 60 | InstrumentReadout usa dois textos fixos ('% da renda' e 'Sem orçamento definido') pensados para o contexto de orçamento, mas o mesmo componente é reusado no dashboard para uma razão de renda — cada página acaba exibindo um rótulo que não corresponde à métrica que o número realmente representa. |
| FIN-008 | 🟡 medium | finance | 30 | Uma transação importada via CSV/PDF não pode ser rastreada de volta ao seu arquivo/lote de origem em nenhuma tela depois que o import é concluído, quebrando o requisito de rastreabilidade da seção financeira. |
| FIN-005 | 🟡 medium | finance | 18.67 | BtgExtratoAdapter segue propagando o sinal de 'Movimentação R$' sob uma suposição documentada como não verificada contra nenhum débito real, e nenhum teste trava esse sinal. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas. |
| FIN-010 | 🟢 low | finance | 4.5 | BudgetEngine#summary usa 0.0 para 'sem base de cálculo' em pct_used, divergindo da convenção nil já adotada em PortfolioService e ReimbursementCoverageCalculator para o mesmo tipo de razão sem denominador válido; o caminho é só alcançável via edição direta na base, não pelo fluxo normal do app. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural de aceitar esse risco (mitigado pela CSP com nonce) ou migrar para cookie HttpOnly + CSRF segue sem resolução formal. |
| SEC-007 | 🟢 low | security | 0.6 | A verificação de dependências Ruby (bundler-audit) e do scanner estático (brakeman) não pôde ser reproduzida neste checkout por falta do `bundle` instalado, então a seção de segurança do lado Rails depende inteiramente do gate de CI já configurado, sem confirmação independente nesta auditoria. |
