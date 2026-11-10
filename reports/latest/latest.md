# Relatório de auditoria — Klipper

> Gerado automaticamente por `render-report.mjs`. Não editar manualmente.

**Trigger:** workflow_run · **Branch:** main · **Commit:** `7e3525de6b56790d15f95d31c3efd07ebab449e1` · **Modo:** fast

## Seções

| Seção | Risco |
|---|---|
| Arquitetura | medium |
| Domínio financeiro | high |
| Segurança | low |

## Possible Regressions

- **FIN-005** — medium → critical: apps/klipper-api/app/services/pdf_adapters/btg_extrato_adapter.rb:15-19 (comentário) e :68 — `amount: BankImport::AmountParser.call(amount_str)` propaga o sinal da string da coluna 'Movimentação R$' sem inversão, sob suposição documentada de que ela já vem com o sinal correto para débito; apps/klipper-api/spec/services/pdf_adapters/btg_extrato_adapter_spec.rb (todo o arquivo) só exercita linhas 'RENDIMENTOS' (crédito) — nenhum teste com valor de débito nessa conta corrente.

## Findings priorizados (RICE)

| ID | Severidade | Categoria | Prioridade | Descrição |
|---|---|---|---|---|
| ARCH-011 | 🟠 high | architecture | 112 | useModal (roteamento de todo modal financeiro) e useToast (todo feedback ao usuário) continuam sem nenhum teste direto — sem mudança desde a última auditoria. |
| FIN-001 | 🟡 medium | finance | 96 | InstrumentReadout rotula qualquer spentRatio recebido como '% da renda', mas em orcamento.vue a razão exibida é gasto/orçamento alocado — o usuário lê 'X% da renda' onde o número real é 'X% do orçamento'. |
| ARCH-009 | 🟡 medium | architecture | 56 | O componente-base compartilhado por todos os modais do app continua sem cobertura de ESC/focus-trap/restauração de foco — sem mudança, e o próprio time já documentou a lacuna no docstring do ModalStress.test.ts em vez de fechá-la. |
| ARCH-004 | 🟡 medium | architecture | 40 | Melhorou parcialmente: ModalNovaConta saiu da lista desde a última auditoria, mas ModalNovoMembro, ModalEditarReembolso e ModalMount continuam sem nenhuma cobertura de teste, direta ou indireta. |
| FIN-008 | 🟡 medium | finance | 25 | Uma transação importada via CSV/PDF não guarda referência ao lote ou arquivo de origem — só dedupe_hash e external_id por linha — então não é possível, depois do fato, provar de qual importação específica ela veio. |
| ARCH-013 | 🟡 medium | architecture | 22.5 | Sem mudança: a terceira reimplementação do sinal buy/sell em sufficient_quantity_for_sell continua fora do teste de paridade existente entre signed_cost e signed_cost_sql, então uma mudança na regra de sinal pode divergir silenciosamente na validação de venda. |
| ARCH-014 | 🟡 medium | architecture | 18 | O padrão visual de campo select customizado continua reimplementado em CSS scoped duplicado por modal de entidade — a contagem de arquivos afetados não diminuiu desde a última auditoria (ainda pelo menos 5), então a dívida piora a cada novo modal de entidade criado sem o componente compartilhado recomendado. |
| SEC-003 | 🟢 low | security | 18 | `devalue`, que motivava este finding na auditoria anterior, não aparece mais no npm audit atual, mas a cadeia de devDependencies transitivas de build/dev (nuxt/@nuxt/nitro-server/@nuxt/vite-builder/esbuild/eslint/archiver) em klipper-web e quebec-web segue com avisos moderate/low sem versão corrigida publicada na linha major atual (nuxt ^3.15.4) — nenhum crítico/high, e o gate de CI (`audit-gate.mjs`, bloqueia só high/critical) permanece verde por desenho. |
| FIN-005 | 🔴 critical | finance | 10.67 | BtgExtratoAdapter assume, sem nenhum caso de teste, que a coluna 'Movimentação R$' já traz o sinal correto para débitos nesta conta corrente investimento; se a suposição estiver errada, todo débito importado dessa fonte entra com o sinal invertido. |
| ARCH-008 | 🟡 medium | architecture | 9.6 | Sem mudança: template e `<style scoped>` de ModalNovoLancamento e ModalEditarLancamento continuam duplicados quase byte a byte. |
| ARCH-005 | 🟢 low | architecture | 8 | Melhorou significativamente: 3 das 4 páginas apontadas na última auditoria (dashboard, contas, orçamento) agora têm teste de página; só portadores.vue continua sem nenhum. |
| ARCH-015 | 🟢 low | architecture | 6 | Sem mudança: a regra 'occurred_on não pode ser futuro' continua duplicada verbatim entre Transaction e Investment em vez de viver no diretório de concerns já existente. |
| FIN-010 | 🟢 low | finance | 6 | BudgetEngine#summary usa 0.0 como fallback de pct_used quando amount_limit não é positivo, mas esse ramo é hoje inalcançável porque Budget exige amount_limit > 0; se essa validação do model mudar, reintroduz a mesma ambiguidade '0% vs sem orçamento' que o resto do domínio já resolve com nil. |
| SEC-005 | 🟢 low | security | 6 | PATCH /api/v1/password_resets/:token (redenção do token de reset de senha) continua sem qualquer rate limiting, ao contrário de todas as outras rotas de autenticação não-autenticadas, permitindo tentativas ilimitadas de adivinhar um token de reset válido por força bruta de IP único. |
| SEC-006 | 🟢 low | security | 2 | O access token da SPA continua exposto a JavaScript via cookie não-httpOnly, e a decisão arquitetural de aceitar esse risco (mitigado pela CSP com nonce) ou migrar para cookie HttpOnly + CSRF segue sem resolução formal — o ADR permanece em `proposed`. |
