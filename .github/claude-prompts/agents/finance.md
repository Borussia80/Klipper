# Finance Agent

Leia primeiro `.github/claude-prompts/_shared-contract.md` — schema de saída,
regra anti-invenção e definição dos campos são obrigatórios e não repetidos
aqui. **Esta é a seção mais crítica do Klipper** — a "Regra de Ouro do
Agente" do `CLAUDE.md` raiz do projeto ("matemática ancora; código sem teste
não entra") se aplica com mais força aqui do que em qualquer outra seção.

## Escopo

Repositório inteiro. Seção = **Domínio financeiro**.

Avalie:
- **Integridade de cálculos**: qualquer soma/subtração/proporção financeira
  (saldos, gastos, orçamento, patrimônio, juros de cartão, rateio de
  reembolso) tem teste unitário cobrindo caso normal + borda (ex: divisão por
  zero, valores negativos, `allocated = 0`)? Trate cálculo sem teste como
  `severity: critical`, `adr_candidate: false` (é bug, não decisão
  arquitetural).
- **Consistência patrimonial**: dado que aparece em mais de um lugar (ex:
  saldo de conta no dashboard vs. em `contas.vue` vs. no relatório de
  patrimônio) é sempre derivado da mesma fonte, ou existe duplicação de
  lógica que pode divergir?
- **Dado inventado na UI**: procure especificamente por valores hardcoded que
  parecem financeiros (strings tipo "R$", percentuais fixos) fora de fixture
  de teste — é exatamente o padrão do bug histórico já corrigido em
  `investimentos.vue` (`PortfolioValueChip`, ver `ROADMAP_KLIPPER_WEALTH_OS.md`
  seção "Bugs conhecidos"). Se encontrar recorrência do padrão, marque
  `severity: critical`.
- **Regras fiscais** (IRPF, categorização fixo/variável/cartão): mudança de
  regra sem atualizar teste correspondente.
- **Rastreabilidade**: toda transação consegue ser rastreada até sua origem
  (import de CSV/PDF, lançamento manual) sem perda de referência?

## Fontes a inspecionar

- `apps/klipper-api/app/services/` (cálculos: `debt_ranking_calculator.rb`,
  `category_recurrence_calculator.rb`, `bank_import/dedupe_hash.rb`, etc.) e
  seus specs em `apps/klipper-api/spec/`.
- `apps/klipper-web/composables/use*Kpis.ts` (`useAccountsKpis.ts`,
  `useBudgetKpis.ts`) e seus testes em `__tests__/`.
- `ROADMAP_KLIPPER_WEALTH_OS.md` — lacunas e bugs financeiros já mapeados
  manualmente; não repita como "novo" o que já está lá como pendência
  conhecida, mas confira se o status descrito ainda bate com o código atual.

## Saída

Escreva o JSON em `$OUTPUT_PATH`, com `"agent": "finance"` e `"section": {
"name": "Domínio financeiro", ... }`.
