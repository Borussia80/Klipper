# Spec 06 — Importação: deduplicação, conciliação, pré-visualização e desfazer

**Onde mora:**
- `ImportBatch`: model; agrupa e permite desfazer.
- `ImportMatcher`: service, porte do algoritmo de `matchTransactions` do Actual.
- `TransactionWriter`: já existe; passa a receber o resultado do matcher em vez de decidir sozinho.

Toda importação (PDF, CSV e, depois, OFX) passa pelo mesmo caminho:
`leitor → linhas normalizadas → matcher → pré-visualização → confirmação → lote`.

## Deduplicação (corrige R2 e R3)

1. **I-1.** Cada linha importada ganha `external_id`:
   - OFX: `FITID`.
   - PDF/CSV: `sha256(conta | data | descrição normalizada | valor | ordinal)`, onde `ordinal` é a posição da linha
     entre as **idênticas do mesmo arquivo** (1ª, 2ª…).
   - Assim, dois cafés iguais no mesmo dia viram ordinal 1 e 2 e **não** colidem, e a mesma fatura reimportada gera os
     mesmos ids e **não** duplica.
2. **I-2.** Unicidade **no banco**: índice único parcial `(account_id, external_id) WHERE external_id IS NOT NULL`.
   Corrige a corrida R11; o `exists?` some.
3. **I-3.** `external_id` **não depende de `account_id` mutável**: ao atribuir conta (`assign_account`), o
   `external_id` é recalculado na mesma operação. Corrige R3. O `dedupe_hash` atual vira `external_id` numa
   migração de dados (ordinal = ordem por `id` dentro do grupo idêntico).
3a. **I-3a.** **Estabilidade do identificador.** O `external_id` depende só do **conteúdo** da linha (conta, data,
    descrição normalizada, valor) e do ordinal **entre linhas idênticas** — nunca do nome do arquivo, da posição da
    linha, da ordem das demais linhas nem da configuração de mapeamento. Assim: renomear o arquivo, reordenar as
    linhas, dividir um extrato em dois ou juntar dois num só produz os mesmos ids. Limite conhecido: se o banco muda a
    descrição de uma linha já importada, ela vira id novo e cai como `provável duplicada` (passada 2), não como
    `nova`. Mudar a regra de normalização de descrição exige migração dos ids existentes.
4. **I-4.** **Três passadas** (ordem do Actual, `server/accounts/sync.ts`), cada lançamento existente casa no
   máximo uma vez:
   1. `external_id` igual na mesma conta → **duplicada**, não importa.
   2. Mesma conta, **mesmo valor**, data a **±7 dias**, descrição normalizada igual → **provável duplicada**
      (desmarcada por padrão na pré-visualização). Entre candidatos, ganha a data mais próxima.
   3. Mesma conta, mesmo valor, ±7 dias, descrição diferente, **e existente sem `external_id`** (lançado à mão) →
      **possível correspondência** (marcada para importar, com aviso "parece com 'X' de DD/MM").
5. **I-5.** Lançamento `previsto` (spec 05) ou parcela prevista (spec 04, K-18) que casa na passada 2 ou 3 é
   **conciliado**: vira `efetivado`, valor e data do arquivo prevalecem, e recebe o `external_id`. Não cria linha nova.
6. **I-6.** Descrição normalizada = minúsculas, sem acento, sem dígitos de autorização/NSU, espaços colapsados.

7a. **I-6a.** Estado `conflito`: mesmo `external_id` na mesma conta com valor ou data diferentes. Fica bloqueado até o
    usuário escolher manter o existente ou atualizá-lo.
7b. **I-6b.** Linha que corresponde a lançamento **excluído** pelo usuário (o `external_id` fica guardado na exclusão)
    vem marcada "excluída antes" e desmarcada; reimportar é escolha explícita.
7c. **I-6c.** A novidade não é decidida por "última data vista": lançamento retroativo publicado depois pelo banco é
    reconhecido como novo.

## Limites da deduplicação sem identificador externo

PDF e CSV dos bancos usados **não trazem** identificador do banco. O `external_id` dessas linhas é derivado do
conteúdo (I-1) e **não distingue** transações indistinguíveis pelos dados disponíveis. O Klipper não promete
deduplicação perfeita nesses casos: sinaliza e o usuário decide.

| Situação | O que o sistema sabe | Estado |
|---|---|---|
| Identificador do banco (FITID) igual | Mesma transação, com certeza | `duplicada` |
| Reimportar o mesmo arquivo, ou um que cobre o mesmo período inteiro | Grupos de linhas idênticas têm o mesmo tamanho dos dois lados | `duplicada` |
| Grupo de linhas idênticas (mesma conta, data, descrição normalizada e valor) com **tamanho diferente** no arquivo e no que já existe | Não dá para saber se é compra repetida ou duplicata | **`ambigua`** para as linhas excedentes |
| Grupo idêntico num **dia de borda** do arquivo (primeiro ou último dia coberto), quando o arquivo anterior também cobria esse dia | O arquivo pode ter cortado o dia no meio; o ordinal pode não corresponder | **`ambigua`** |
| Mesmo gasto vindo de duas fontes (PDF da fatura e lançamento manual, ou PDF e CSV com descrições diferentes) | Só valor e data próximos | `correspondencia` (passada 3), nunca `duplicada` |

Estado **`ambigua`**: bloqueado até decisão explícita ("é outra compra" → cria; "é a mesma" → não cria). A tela
mostra lado a lado as linhas do arquivo e as existentes do grupo. Nada é descartado nem criado sem a escolha.



7. **I-7.** PDF já tem preview com linha assinada (`RowSigner`). CSV e OFX passam a ter o mesmo fluxo: nada é
   gravado antes de confirmar.
8. **I-8.** Cada linha mostra: data, descrição, valor, categoria sugerida (spec 07), `kind` sugerido (spec 03, L-12)
   e o resultado do matcher (`nova` · `duplicada` · `provável duplicada` · `ambígua` · `concilia com previsto`).
8a. **I-8a.** **A pré-visualização é guardada no banco**, não só devolvida ao cliente: `import_batch` nasce com
    `status: preview` e cada linha vira um `import_row` (dados normalizados, resultado do matcher, decisão do
    usuário, checksum do arquivo e referência da linha no arquivo). Confirmar muda o lote para `confirmed` numa
    transação só. Cancelar não cria lançamento. Confirmar duas vezes o mesmo lote é recusado (idempotente).
    Substitui a assinatura por linha do PDF (`RowSigner`) pelo mesmo efeito: o cliente só manda decisões, não valores.
9. **I-9.** **CSV:** se os cabeçalhos não casarem com os aliases atuais, a tela pede o mapeamento (data, descrição,
   valor; ou débito e crédito em colunas separadas; formato de data). O mapeamento fica salvo por conta para a
   próxima vez.

## Desfazer

10. **I-10.** Toda confirmação cria um `import_batch` (`account_id`, `source`, `filename`, `rows_imported`,
    `created_at`) e cada linha gravada leva `import_batch_id`.
11. **I-11.** **Desfazer** apaga as linhas criadas pelo lote e **reverte** as conciliações (previsto conciliado volta
    a previsto, sem `external_id`). Recusado se alguma linha do lote já foi **conciliada com o banco** (spec 02) — a
    tela lista quais.
12. **I-12.** Desfazer é permitido por 30 dias; depois o lote fica só como histórico.

## OFX (importante; porte P6 do plano de UX)

13. **I-13.** Leitor de OFX 1.x (SGML) e 2.x (XML), com `FITID` como `external_id`, `DTPOSTED` como data,
    `TRNAMT` com sinal. Portado do ezBookkeeping (`pkg/converters/ofx/`), MIT.
14. **I-14.** QFX e QIF só entram quando houver arquivo real (anonimizado) de um banco brasileiro para servir de
    fixture. Sem isso, o leitor seria testado contra um formato imaginado.

## Casos de teste (RSpec)

```ruby
# spec/services/import_matcher_spec.rb
# mesmo arquivo com 2 linhas "CAFE X 5,00 10/10" → 2 lançamentos (ordinais 1 e 2)       (hoje: 1 — R2)
# reimportar o mesmo arquivo → 0 novos, 2 duplicadas
# importar sem conta, assign_account, reimportar com conta → 0 novos                      (hoje: duplica — R3)
# existente manual "Mercado" 350,00 em 06/10; importado "SUPERMERCADO ABC" 350,00 em 08/10 → possível correspondência
# existente com external_id e importado com external_id diferente, mesmo valor/data → nova (não casa na passada 3)
# um existente e dois importados iguais a ele → um casa, o outro é novo
# previsto aluguel 2500 em 05/10; importado 2500 em 06/10 → concilia, previsto vira efetivado
# arquivo com 3 linhas "CAFE X 5,00 10/10" e 2 já existentes iguais → 2 duplicadas + 1 ambigua (bloqueada)
# arquivo de 10–20/10 após outro de 01–10/10, com "CAFE X" idêntico em 10/10 → ambigua, não duplicada
# ambigua decidida "é outra compra" → cria; "é a mesma" → não cria; sem decisão → confirmação recusada
# corrida: dois writers com o mesmo external_id → um grava, o outro recebe RecordNotUnique e conta como duplicada

# spec/services/import_batch_undo_spec.rb
# desfazer apaga as 12 criadas e devolve os 2 previstos a previsto
# lote com 1 linha conciliada com o banco → recusa e lista a linha
# lote com 31 dias → recusa
```
