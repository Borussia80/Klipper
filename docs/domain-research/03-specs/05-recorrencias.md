# Spec 05 — Recorrências e agendamentos

**Onde mora:**
- `RecurrenceRule`: puro (`app/lib`). Dado o padrão, devolve as datas num intervalo.
- `ScheduledTransaction`: model.
- `ScheduledOccurrencesCalculator`: consulta (porte P3 do plano de UX). Materializa só as próximas ocorrências como
  `previsto`.

**Sem job.** O Render Free hiberna e o uso é local, então nada depende de cron. As ocorrências são calculadas
sob demanda, ao abrir o painel ou o fluxo projetado.

Substitui a Fatia 6 de UX, que fica dependente desta spec.

## Regras

1. **R-1.** Um agendado tem: conta, categoria, descrição, valor, `kind` (regular ou transfer), início, fim opcional
   (data ou número de ocorrências), padrão e `confirmacao` (`manual` | `automatica`).
2. **R-2.** Padrões:

| Padrão | Parâmetros | Exemplo |
|---|---|---|
| `mensal_dia` | dia 1–31 | aluguel dia 5 |
| `mensal_ultimo_dia` | — | |
| `mensal_dia_util` | n-ésimo dia útil (1 = primeiro, −1 = último) | salário no 5º dia útil |
| `semanal` | dia da semana, a cada k semanas | diarista |
| `anual` | dia e mês | IPVA, seguro |
| `intervalo` | a cada k dias / meses | |

3. **R-3.** **A data base não acumula erro.** A ocorrência k de "mensal dia 31" a partir de 31/01 é
   `início + k meses` com o dia ajustado (spec 04, K-2), **não** "a anterior + 1 mês": a segunda dá 31/01 → 28/02 →
   28/03, quando o certo é 28/02 → **31/03**.
4. **R-4.** **Ajuste de dia não útil**, por agendado: `nenhum` (padrão) · `proximo_util` · `util_anterior`. Contas de
   consumo costumam ir para o próximo dia útil; salário, para o anterior.
5. **R-5.** **Geração.** O calculator materializa como `previsto` (spec 03) as ocorrências **até hoje + 60 dias**
   que ainda não existem (`scheduled_transaction_id` + `occurrence_date` é única). Ocorrência passada não confirmada
   fica `previsto` e aparece como "atrasada".
6. **R-6.** `confirmacao: automatica` → no cálculo, ocorrência com data ≤ hoje vira `efetivado` sozinha. Indicada só
   para débito automático; o padrão é `manual`.
7. **R-7.** **Conciliação com extrato importado** (spec 06): uma linha importada da mesma conta, valor dentro de
   ±7,5 % (o limiar `isapprox` do Actual) e data a ±5 dias de um previsto é **sugerida** como a efetivação dele. O
   usuário confirma. Automática só depois (registrado no plano de UX).

## "Só esta" × "esta e as próximas"

8. **R-8.** **Só esta:** altera a linha `previsto` daquela data, marcando `detached: true`. O agendado não muda e não
   regera a linha.
9. **R-9.** **Esta e as próximas:** encerra o agendado atual na véspera (`fim = data − 1`) e cria um novo, a partir
   desta data, com os valores novos. Previstos futuros do antigo são apagados e regerados pelo novo. Efetivados não
   são tocados.
10. **R-10.** **Excluir agendado:** apaga os previstos futuros não `detached`; efetivados ficam.

11. **R-11.** **Pausar** suspende a geração; **retomar** volta a gerar a partir de hoje, sem gerar as ocorrências do
    período pausado. Nenhuma ocorrência depende de um processo ter rodado num dia específico: abrir o app depois da
    data mostra a ocorrência como prevista atrasada.

## Casos de borda

| Caso | Regra |
|---|---|
| Mensal dia 31 a partir de 31/01/2026 | 31/01, 28/02, 31/03, 30/04, 31/05… |
| Mensal dia 29 em ano não bissexto | 28/02 |
| 5º dia útil de novembro/2026 | 01/11 é domingo; 02/11 feriado → 03, 04, 05, 06, 09 → **09/11** |
| Último dia útil de outubro/2026 | 31/10 é sábado → **30/10** |
| Dia 1º de maio/2026 com `proximo_util` | 01/05 é feriado (sexta) → **04/05** |
| Agendado com fim antes do início | Recusado |
| Valor alterado "só esta" e depois "esta e as próximas" numa data anterior | A `detached` permanece como está |

## Casos de teste (RSpec)

```ruby
# spec/lib/recurrence_rule_spec.rb
RecurrenceRule.mensal_dia(31, from: Date.new(2026,1,31)).take(5)
  # => [2026-01-31, 2026-02-28, 2026-03-31, 2026-04-30, 2026-05-31]
RecurrenceRule.mensal_dia_util(5).on(2026, 11)   # => 2026-11-09
RecurrenceRule.mensal_dia_util(-1).on(2026, 10)  # => 2026-10-30
RecurrenceRule.mensal_dia(1, ajuste: :proximo_util).on(2026, 5) # => 2026-05-04
RecurrenceRule.anual(29, 2).on(2027)             # => 2027-02-28

# spec/services/scheduled_occurrences_calculator_spec.rb
# chamar duas vezes não duplica (índice único)
# hoje + 60 dias: gera 2 ocorrências mensais, não 12
# automatica com data passada → efetivado; manual → previsto atrasado
# "esta e as próximas" em 05/12: antigo termina 04/12, novo começa 05/12, efetivados intocados
# excluir agendado: previstos futuros somem, detached e efetivados ficam
```
