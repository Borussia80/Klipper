# Especificação funcional clean-room — núcleo financeiro do Klipper · v2

**Destinatário:** quem implementa. Não exige nem permite consulta a projetos de terceiros ou a relatórios de
pesquisa. Substitui a v1 (que continua válida no que esta não altera) e complementa as specs de
`docs/domain-research/03-specs/`, que são a fonte das regras numeradas citadas aqui (C-, L-, K-, R-, I-, G-, O-).
Ordem e escopo: `docs/domain-research/05-plano-implementacao.md`.

Convenção do Klipper (mantida): `amount > 0` sempre; a direção vem de `transaction_type` (`debit` sai da conta,
`credit` entra) e o significado de negócio vem de `kind`.

---

## M1. Lançamentos e grupos ligados

**Responsabilidade:** registrar fatos financeiros e garantir que grupos de linhas ligadas sejam coerentes.

**Entidades:** lançamento (conta, data, valor, direção, `kind`, `status`, origem); grupo ligado = par de transferência
ou pai + filhos de split.

**Invariantes**
1. Valor com sinal de uma linha: `+amount` se `credit`, `−amount` se `debit`.
2. **Par de transferência:** duas linhas, contas diferentes do mesmo usuário, direções opostas. Na mesma moeda, a soma
   com sinal é **exatamente 0**. Em moedas diferentes, cada linha está na moeda da sua conta e a taxa gravada
   satisfaz `|valor_destino − valor_origem × taxa| ≤ 0,005` na moeda de destino.
3. **Split:** Σ filhos = pai, exatamente, em centavos. O pai não entra em nenhuma soma.
4. Num split, no máximo **uma** parte pode ser enviada sem valor; ela recebe `pai − Σ demais` e precisa resultar > 0.
5. Nenhum lançamento `efetivado` ou `conciliado` tem data futura; `previsto` pode.

**Operações permitidas:** criar, editar, excluir (com as restrições de M6), dividir, desfazer divisão.

**Rejeitadas:** transferência para a mesma conta; split com soma diferente; duas partes sem valor; parte com valor
≤ 0; linha de outro usuário em qualquer grupo.

**Falha e concorrência:** criar ou alterar um grupo é uma transação de banco: ou todas as linhas mudam, ou nenhuma.
Duas edições simultâneas do mesmo grupo: a segunda falha por conflito de versão (lock otimista), não sobrescreve.

**Aceitação**
- Transferência de 100 de A para B: A −100, B +100, receita e despesa do mês inalteradas.
- Split 100 → 60 + 40: qualquer total do mês conta 100 uma vez.
- Split 100 → 60 + (sem valor): a segunda parte vale 40.
- Split 100 → 60 + 50: rejeitado, nada gravado.
- Falha forçada na gravação da segunda linha: nenhuma linha persiste.

## M2. Contas, saldos e conferência

**Responsabilidade:** saldo em qualquer data, explicável e protegido depois de conferido.

**Fórmula:** `saldo(conta, d) = saldo_inicial + Σ valor_com_sinal(t)` para `t` da conta, `status ∈ {efetivado,
conciliado}`, `t.data ≤ d`, excluindo pais de split. Saldo previsto inclui `previsto`. Em conta de passivo o resultado
negativo é a dívida.

**Invariantes**
1. O saldo nunca é digitado; é sempre derivado (C-3).
2. **Conferência:** dado `saldo_banco` numa data `d`, `diferença = saldo_banco − saldo(conta, d)`. Se ≠ 0, cria-se um
   lançamento de ajuste visível em `d` (fora de receita/despesa). Depois disso `saldo(conta, d) = saldo_banco`.
3. Cada conferência é um registro datado e permanente (data, saldo informado, diferença, ajuste, autor). Desfazer
   marca o registro como desfeito; não apaga.
4. Nova conferência só em data **posterior** à última conferência ativa da conta (C-10a).
5. Linha conferida não muda valor, data, conta nem direção; descrição, categoria e notas podem mudar.
6. Desequilíbrio nunca some: toda diferença aceita vira ajuste visível; não há arredondamento silencioso.

**Rejeitadas:** conferir em data anterior à última ativa; editar campo financeiro de linha conferida; arquivar conta com
saldo ≠ 0 sem ajuste confirmado; excluir conta com lançamentos.

**Concorrência:** conferências da mesma conta são serializadas (lock da linha da conta).

**Aceitação (casos sintéticos)**
- Abertura 1.000 em 01/01; débito 120 em 05/01 → `saldo(05/01) = 880`.
- Depois, débito 30 em 03/01 → `saldo(05/01) = 850`; `saldo(02/01) = 1.000`.
- Só com o primeiro caso (saldo calculado de 880 em 05/01), o banco informa 870 → ajuste −10 em 05/01, `saldo(05/01) = 870`, os
  lançamentos anteriores intactos e o registro da conferência consultável.
- Tentar conferir 02/01 depois disso → rejeitado.
- Tentar alterar o valor do débito de 120 (conferido) → rejeitado; alterar a categoria → aceito.

## M3. Patrimônio e histórico

**Fórmula:** `patrimônio(d) = Σ saldo(c, d)` para todas as contas existentes em `d`; contas de passivo entram com
saldo negativo. Investimento entra pelo valor datado quando houver, senão pelo custo, rotulado como custo.

**Invariantes:** conta arquivada sai do total atual e continua nos pontos anteriores ao arquivamento; o histórico
guardado é cache e pode ser recalculado a partir dos lançamentos com o mesmo resultado.

**Aceitação:** ativos 10.000 e cartão −2.500 → 7.500, também consultado em data passada; inserir um lançamento
retroativo e recalcular → todos os pontos posteriores mudam pelo mesmo valor, os anteriores não.

## M4. Importação e normalização

**Responsabilidade:** transformar um arquivo numa lista de linhas normalizadas, sem gravar lançamento.

**Contrato da linha normalizada:** conta, data, valor (decimal exato, > 0), direção, descrição original, descrição
normalizada, identificador externo, formato de origem, checksum do arquivo, referência da linha no arquivo, sugestões
(categoria, `kind`) e avisos.

**Regras**
1. Identificador externo: o do arquivo, quando confiável (OFX), ou o hash de conta + data + descrição normalizada +
   valor + **ordinal** entre linhas idênticas do mesmo arquivo (I-1).
2. O identificador depende da conta atual; ao reatribuir a conta, é recalculado na mesma operação (I-3).
3. Reimportar um arquivo cuja linha corresponde a um lançamento **excluído** pelo usuário: a linha vem marcada
   "excluída antes" e desmarcada; o usuário pode reimportá-la explicitamente.
4. Uma configuração de mapeamento (colunas, data, separador decimal, débito/crédito) é salva por conta e reaplicada.
5. A janela de novidade **não** é definida por "última data vista": lançamento retroativo publicado depois tem de ser
   reconhecido como novo.

**Rejeitadas:** linha sem data, valor ou descrição (vira registro inválido, com motivo); valor ambíguo que o parser
não decide (ex.: `1.234` sem configuração de formato numa conta que já mostrou os dois formatos).

## M5. Conciliação de importação

**Saídas por linha (estados explícitos):**

| Estado | Condição | Padrão na tela | Ação ao confirmar |
|---|---|---|---|
| `nova` | Nenhuma correspondência | marcada | cria |
| `duplicada` | Mesmo identificador externo na mesma conta | desmarcada, sem opção de forçar | nada |
| `provavel_duplicada` | Mesma conta e valor, data ±7 dias, mesma descrição normalizada | desmarcada | nada, salvo se o usuário marcar |
| `correspondencia` | Mesma conta e valor, ±7 dias, descrição diferente, existente sem identificador externo (lançado à mão) ou `previsto` | marcada como "vincular" | vincula: o existente recebe o identificador e vira `efetivado`; não cria linha |
| `ambigua` | Linhas idênticas (conta, data, descrição normalizada, valor) sem identificador do banco, em quantidade diferente no arquivo e no existente, ou num dia de borda do período do arquivo já coberto antes | bloqueada até decisão | "outra compra" cria; "a mesma" não cria |
| `conflito` | Mesmo identificador externo com valor ou data diferentes | bloqueada até decisão | o usuário escolhe manter ou atualizar |
| `invalida` | Falha de normalização | bloqueada | nada |
| `ignorada` | Usuário desmarcou | — | nada, registrado |

**Limite declarado:** sem identificador do banco, transações indistinguíveis pelos dados não são deduplicadas com
certeza; o sistema sinaliza `ambigua` e não decide sozinho.

**Invariantes:** cada lançamento existente casa com no máximo uma linha importada; entre candidatos, a data mais
próxima; **nunca** se exclui nem se funde lançamento automaticamente.

**Falha e concorrência:** confirmação é uma transação; a unicidade (conta, identificador externo) é garantida por
índice único; violação na confirmação conta como `duplicada`, não como erro. Confirmar duas vezes o mesmo lote é
recusado.

**Aceitação**
- Mesmo arquivo duas vezes → segunda vez 0 novas.
- Arquivo de 01–15/10 e depois de 10–31/10 → os de 10–15 aparecem como `duplicada`.
- Duas compras de 50,00 iguais no mesmo dia → as duas entram.
- Arquivo com 3 compras idênticas no dia e 2 já registradas → 2 `duplicada`, 1 `ambigua` que exige decisão.
- Lançamento manual "Mercado 350,00" em 06/10 e importado "SUPERMERCADO 350,00" em 08/10 → `correspondencia`.
- Arquivo do banco publica em novembro um lançamento datado de 05/10 → `nova`.
- Duas confirmações simultâneas do mesmo arquivo → cada linha gravada uma vez.
- Falha na linha 7 de 10 → nada gravado; o lote volta à pré-visualização com o erro na linha 7.

## M6. Correção e reversão

1. Lançamento `conciliado` não é excluído: corrige-se com um lançamento de reversão (mesmo valor, direção oposta,
   ligado ao original). Os dois aparecem.
2. `efetivado` não conferido pode ser excluído; a exclusão é auditada (ids, conta, data, valor, sem descrição
   bancária).
3. Excluir uma linha de transferência exclui as duas, com confirmação.

**Aceitação:** excluir despesa de 50 em data passada → saldos posteriores +50 e um registro de auditoria; reverter
lançamento conferido de 120 → saldo atual +120, original e reversão visíveis.

## M7. Motor de regras

**Responsabilidade:** sugerir e aplicar campos (categoria, `kind`, portador, descrição) a lançamentos novos, de forma
determinística e explicável. **Um só motor**: as regras fixas atuais viram regras padrão dentro dele.

**Regras**
1. Regra = condições tipadas (descrição: é / contém / começa com / um de; valor: é / aproximadamente ±7,5 % / entre /
   maior / menor; conta: é / um de; direção) combinadas por E, + ações tipadas + ativa + origem (usuário, aprendida,
   padrão).
2. Ordem determinística por especificidade (G-4), empate pela mais nova, usuário antes de padrão.
3. **Avaliação sobre o estado original:** todas as condições são avaliadas sobre o lançamento **como chegou**; uma
   ação não altera o que as regras seguintes veem. Por campo, a primeira regra que o define vence.
4. Aplica-se **só** a lançamento novo (manual sem categoria e importado). Editar um lançamento não reaplica regras.
5. Reaplicação a existentes é ação explícita com pré-visualização.
6. Ação que referencia categoria/conta/portador inexistente ou de outro usuário é rejeitada **ao salvar a regra**.
7. Cada aplicação grava: lançamento, regra, campo, valor anterior, valor novo, data. A tela mostra "categoria definida
   pela regra X".
8. Aprendizado (G-10 a G-12): 3 votos nos 5 recentes da mesma descrição; regra aprendida apagada não volta.

**Rejeitadas:** regra sem condição; ação sem parâmetro válido; ciclo é impossível por construção (regra não reavalia
sobre resultado de outra).

**Aceitação**
- Regra A (descrição é "uber *trip" → Lazer) e B (contém "uber" → Transporte) → Lazer, e o registro aponta A.
- A define categoria; B define categoria e portador → categoria de A, portador de B.
- A renomeia a descrição para "Mercado"; B tem condição "descrição contém mercado" → B **não** dispara (estado
  original).
- Usuário corrige a categoria → nenhuma regra reaplica.
- Regra apontando para categoria de outro usuário → rejeitada ao salvar.

## M8. Recorrências

**Regras (R-1 a R-10)** e, além delas:
1. Ocorrências calculadas **sob demanda** até hoje + 60 dias; nenhuma depende de um processo ter rodado num dia
   específico.
2. Unicidade (agendado, data da ocorrência) garantida por índice único.
3. Pausar: ocorrências futuras não geradas; retomar: volta a gerar a partir de hoje, sem gerar retroativamente as do
   período pausado.
4. Alterar o agendado não toca ocorrências efetivadas.

**Aceitação:** mensal dia 31 a partir de 31/01/2026 → 31/01, 28/02, 31/03, 30/04, 31/05; abrir o app só em 02/05 →
a ocorrência de 30/04 existe (atrasada, prevista); calcular duas vezes → sem duplicata; 5º dia útil de novembro/2026
→ 09/11 (02/11 é feriado); 1º de maio de 2026 com "próximo dia útil" → 04/05.

## M9. Orçamento

**Regras (O-1 a O-6):** limite mensal por categoria; gasto = débitos regulares − estornos, por competência;
transferência, pagamento de fatura e ajuste não entram; rollover opcional só de sobra positiva; estouro não reduz o
mês seguinte; sem limite → "sem limite", não 0 %.

**Aceitação:** limite 1.000 com rollover; setembro gasta 850 → outubro limite 1.150; outubro gasta 1.200 com estorno de
80 → gasto 1.120, restante 30. Reembolso de terceiro (renda) não abate o gasto da categoria; estorno do
estabelecimento abate.

## M9a. Cartão: data da compra e mês de contabilização

- A data da compra (`occurred_on`) é o fato financeiro e nunca é alterada; todas as parcelas guardam a data da compra.
- Mês de contabilização de toda linha de cartão = mês do vencimento da fatura em que ela está; é derivado e muda só
  quando a linha muda de fatura. Fora do cartão = mês da data.
- Orçamento e relatórios mensais usam o mês de contabilização; fluxo de caixa usa a data de vencimento; lista,
  busca, saldo por data e deduplicação usam a data da compra.

**Aceitação** (fecha dia 3, vence dia 10): compra em 02/10/2026 → contabilizada em outubro; em 03/10/2026 →
novembro; a lista mostra 02/10 e 03/10. Compra de 7× em 15/10 → 7 parcelas com data 15/10, contabilizadas de novembro
a maio. Mover uma compra para a fatura seguinte → muda o mês de contabilização, a data continua a mesma.

## M10. Dinheiro e precisão

- Decimal exato a 2 casas no banco; meio-par só no resultado final; divisão em N partes por centavos com resto
  atribuído (D-4). Exemplos: 100,00 em 3 → 33,34 + 33,33 + 33,33; 1.000,00 em 7 → 142,90 + 6 × 142,85.
- `1.234,56` = 1234,56; `1,234.56` = 1234,56; `1.000` = 1000 (convenção BR); `1.5` = 1,5.
- Moeda estrangeira: valor sempre na moeda da conta; valor original, moeda, taxa, data e fonte da taxa preservados;
  taxa nunca recalculada depois (salvo substituir estimativa pelo valor real da fatura); total consolidado devolve
  as taxas usadas; sem cotação → recusa, nunca soma como BRL. Detalhe por caso em
  `docs/domain-research/03-specs/01-dinheiro-e-datas.md`, "Semântica de moeda".

## Segurança e integridade (todos os módulos)

- Toda consulta e mutação é escopada pelo usuário autenticado; id de outro usuário → 404 e nada alterado.
- Logs e auditoria guardam ids, decisão e checksum; nunca descrição bancária, payload bruto ou credencial.
- Arquivo importado: tamanho máximo, verificação de tipo, sem execução de conteúdo; o original não é logado.
- Toda operação que cria mais de uma linha é atômica.

## Suíte mínima de cenários (cada um vira spec própria)

| # | Cenário | Módulo |
|---|---|---|
| 1 | Abertura de saldo e saldo no dia anterior | M2 |
| 2 | Receita e despesa no mês | M1, M9 |
| 3 | Transferência na mesma moeda e entre moedas | M1 |
| 4 | Lançamento com várias partes (split 3 vias) | M1 |
| 5 | Split com soma correta, incorreta e com parte implícita | M1 |
| 6 | Movimento retroativo e recálculo | M2, M3 |
| 7 | Conferência com diferença, conferência antiga recusada, reversão | M2, M6 |
| 8 | Conta em USD no patrimônio | M3, M10 |
| 9 | Arredondamento: divisão em parcelas e meio-par | M10 |
| 10 | Reimportação do mesmo arquivo | M5 |
| 11 | Arquivos sobrepostos | M5 |
| 12 | Duplicidade ambígua (dois candidatos, um vence pela data) | M5 |
| 13 | Conciliação com manual e com previsto | M5 |
| 14 | Retroativo publicado depois | M4, M5 |
| 15 | Regras conflitantes e regra que mudaria condição de outra | M7 |
| 16 | Recorrência dia 31, dia útil, feriado, app fechado no dia | M8 |
| 17 | Orçamento com reembolso de terceiro e estorno | M9 |
| 18 | Falha parcial na importação | M5 |
| 19 | Concorrência entre duas confirmações | M5 |
| 20 | Saldo e patrimônio reconstruídos em data passada | M2, M3 |
| 21 | Excluído não volta sem pedido explícito | M4 |
| 22 | Isolamento entre usuários em cada endpoint | todos |

## Limites de implementação

- Não usar código, testes, fixtures, pseudocódigo, comentários ou estrutura interna de projetos de terceiros.
- Usar a arquitetura do Klipper (Rails, PostgreSQL, API JSON, Nuxt) e dados sintéticos.
- Dinheiro em `decimal`, nunca ponto flutuante.
