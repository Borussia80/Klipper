# Spec 15 — Categorização medida contra outubro (taxa de acerto)

**Status:** rascunho de 2026-10-19, aguarda aprovação. **Origem:** backlog de 18/10, item 3 (P0), UR-3.
**Sprint:** D7. **Estende:** spec 07 (`RuleEngine`, aprendizado). **Onde mora:** `CategorizationEvaluator` (service
puro) e a rake `categorization:evaluate` (só lê; nunca grava).

Hoje o `AutoCategorizerService` é uma lista fixa de regex e ninguém sabe o quanto acerta. Sem número, o D7 não tem
critério de "ficou melhor". O gabarito já existe: os lançamentos de outubro que o Roberto classificou à mão.

## Regras

1. **Q-1.** **Gabarito** = lançamentos do usuário no período, `kind: regular`, com categoria definida **por ação do
   usuário** (não por sugestão automática aceita sem edição). Transferência, pagamento de fatura, ajuste e estorno
   ficam fora (não são categorização).
2. **Q-2.** **Sugestão** = o que o categorizador devolveria para a descrição, **sem ver a categoria final** do
   lançamento avaliado. O avaliador recalcula; não lê a sugestão que ficou gravada.
3. **Q-3.** Três contagens por rodada, sempre as três: **acertou** (sugestão = categoria final), **errou** (sugeriu
   outra) e **sem sugestão**. Acerto = acertou ÷ elegíveis; **cobertura** = (acertou + errou) ÷ elegíveis. Um
   categorizador que só sugere o óbvio tem acerto alto e cobertura baixa, e os dois números aparecem juntos.
4. **Q-4.** **Sem vazamento:** regra aprendida (spec 07) só pode usar correções **anteriores ao período avaliado**.
   Avaliar outubro com regras aprendidas das correções de outubro mede memória, não generalização. A rake recusa a
   rodada se detectar regra aprendida criada dentro do período.
5. **Q-5.** **Determinismo:** mesma base e mesmas regras dão o mesmo número. Sem rede, sem modelo externo, sem
   aleatoriedade (spec 07: fuzzy + regras locais, não ML).
6. **Q-6.** Saída: totais (Q-3), **erros listados** (descrição, sugerida, final, valor) e acerto por categoria, para
   o Roberto ver o que corrigir. Nada é gravado; a saída é para leitura.
7. **Q-7.** **Meta** configurável; padrão **80 % de acerto sobre os elegíveis**, e é um chute. Ela só vale depois que o
   Roberto a confirmar (pergunta aberta do backlog). Abaixo da meta a rake sai com código diferente de zero, para o CI
   poder usá-la depois; o D7 não é bloqueado por ela até a meta ser aprovada.
8. **Q-8.** O gabarito é **dado real e fica fora do Git**. Os testes usam fixture **sintética** com a mesma forma
   (descrições inventadas, categorias do plano de contas padrão); o número de outubro só existe na máquina do
   Roberto, na saída da rake.
9. **Q-9.** Primeira rodada, antes de mexer em qualquer regra: **linha de base** do categorizador atual. Todo ajuste
   do D7 é comparado com ela; "melhorou" sem número não vale.

## Casos de teste

```ruby
# spec/services/categorization_evaluator_spec.rb   (fixture sintética)
# 10 lançamentos classificados à mão, categorizador acerta 7, erra 1, não sugere 2
#   → acerto 7/10 = 70 %, cobertura 8/10 = 80 %
# transferência, pagamento de fatura e estorno no período → fora dos elegíveis
# categoria aceita da sugestão sem edição → fora do gabarito (Q-1)
# sugestão gravada no lançamento difere da recalculada → vale a recalculada (Q-2)
# regra aprendida criada dentro do período → rodada recusada (Q-4)
# duas rodadas com a mesma base → resultados idênticos (Q-5)
# spec/lib/tasks/categorization_evaluate_rake_spec.rb
# rake não altera nenhuma categoria nem cria registro (contagem de linhas antes = depois)
# acerto abaixo da meta → código de saída ≠ 0; acima → 0
```

**Perguntas abertas:** (a) a meta de 80 % está certa? (b) o período do gabarito é só outubro ou 16/09 a 17/10, como
os extratos? (c) lançamento que o Roberto reclassificou depois de uma sugestão errada entra no gabarito (proposta:
sim, com a categoria final).
