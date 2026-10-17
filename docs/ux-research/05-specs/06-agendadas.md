# Spec 06 — Lançamentos agendados

**Rota nova:** `/agendados` (item na barra lateral e na folha "Mais" do mobile). · **Prioridade:** 3 ·
**Referências:** modelo e geração E2, lista por vencimento C5.

## Objetivo

Registrar compromissos que se repetem (aluguel, escola, assinaturas, salário) uma vez, ver o que vem pela frente e
alimentar o alarme de vencimento.

## Diferença deliberada em relação ao ezBookkeeping

O ezBookkeeping **cria a transação sozinho** a cada 15 min. O Klipper roda no Render Free, que hiberna, e importa
extratos: lançar sozinho criaria duplicata com o extrato importado. Por isso:
- O agendamento gera **ocorrências previstas**, não transações.
- Ao importar extrato, a ocorrência prevista é **conciliada** com a transação real (mesmo valor ± 5 %, ±3 dias,
  descrição parecida — fuzzy, coerente com o `AutoCategorizerService`).
- Ocorrência vencida sem conciliação vira aviso: "Aluguel previsto para 10/10 ainda não apareceu."
- Botão "Lançar agora" converte a ocorrência em transação manualmente.

## Lista

Duas seções: **Próximos 30 dias** (ocorrências, ordenadas por data, com saldo previsto acumulado da conta à direita)
e **Todos os agendamentos** (regras). Linha de ocorrência: data · descrição · conta · valor · status
(prevista / conciliada / atrasada).

Saldo previsto negativo em alguma data → a linha daquela data recebe **alto**: "Saldo previsto da {conta} fica
negativo em {data}."

## Formulário de agendamento

Campos: tipo, valor, descrição, categoria, conta, portador · **Repete:** mensal (dia N; "último dia útil" fica para
depois), semanal (dia da semana), anual, a cada N dias · **Começa em** (obrigatório) · **Termina em** (opcional) ou
**após N vezes**. Prévia ao vivo: "Próximas: 10/11, 10/12, 10/01."

## Dados — tudo novo

- Tabela `scheduled_transactions`: `user_id`, campos de transação, `frequency` (enum: daily, weekly, monthly,
  yearly, every_n_days), `frequency_value` (dia ou N), `starts_on`, `ends_on`, `occurrences_limit`, `active`.
  Modelo inspirado em E2 (`pkg/models/transaction_template.go`).
- Ao entrar esta tabela, o `CategoryMergeService` (spec 07) passa a mover também
  `scheduled_transactions.category_id`.
- Serviço `ScheduledOccurrencesCalculator` (Ruby): datas de ocorrência num intervalo — **porte** da lógica de
  frequência do E2.
- Conciliação: `parent`/vínculo entre transação real e agendamento (`scheduled_transaction_id` + `occurs_on` em
  `transactions`).
- Endpoints: CRUD `/scheduled_transactions`, `GET /scheduled_transactions/upcoming?days=30`,
  `POST /scheduled_transactions/:id/post_now`.

## Critérios de aceite

1. Mensal dia 31 em fevereiro cai no último dia do mês (unidade).
2. Importar extrato com o aluguel concilia a ocorrência e não duplica.
3. Saldo previsto negativo aparece aqui e no painel como alto.
4. Desativar um agendamento remove as ocorrências futuras da lista sem apagar transações passadas.
