# Spec 10 — Importadores de extrato de conta: Santander, Nubank conta e Caixa

**Status:** rascunho de 2026-10-19, aguarda aprovação. **Origem:** backlog de 18/10, lacuna 1 (P0).
**Estende:** spec 06 (todo leitor entra em `leitor → linhas normalizadas → matcher`). **Sprint:** logo após o D1,
antes do D2 (o D2 precisa do saldo real dessas contas).
**Onde mora:** `app/services/bank_import/` (um leitor por formato) e `Registry` (escolha pelo conteúdo, não pelo nome).

Hoje existem adapters de Itaú, fatura Nubank e BTG. Os extratos de conta mais usados caem no CSV genérico.

## Regras

1. **X-1.** Cada leitor devolve as mesmas linhas normalizadas dos adapters atuais (data, descrição, valor com sinal,
   `external_id` se o formato tiver, saldo após a linha se existir). Nada de regra de negócio no leitor.
2. **X-2.** **Santander CSV:** separador `;`, codificação latin-1 (com BOM), sete linhas de cabeçalho antes de
   `Data;Descrição;Detalhe;Valor;Saldo`, valor no formato `-R$ 1.234,56`. A codificação é detectada, não suposta;
   arquivo que não decodifica é recusado com mensagem, nunca importado com caracteres trocados.
   **Achado de 2026-10-19:** o extrato real enviado pelo Roberto é **PDF** (2 páginas, com camada de texto), não CSV.
   O leitor prioritário é o adapter de PDF X-2a; o CSV segue especificado, mas sem amostra real.
2a. **X-2a.** **Santander PDF** (estrutura observada, sem copiar dados): título "EXTRATO DE CONTA", agência, conta,
   período, quadro com saldo inicial, entradas, saídas e saldo final, e "DETALHE DOS MOVIMENTOS" agrupado por dia com
   cabeçalho "<dia da semana>, DD de <mês> de AAAA". Cada movimento ocupa **três linhas**: descrição ("Pix enviado",
   "Pix recebido", "Pix devolvido", "Pagamento cartao credito"…); data, valor (`-R$ 1.234,56`) e saldo após a linha;
   contraparte **truncada em ~21 caracteres**. Ordem do mais novo para o mais antigo. O saldo final do quadro é o
   saldo confirmado (X-6). Conferência: saldo inicial + entradas − saídas = saldo final.
3. **X-3.** **Santander xlsx:** mesmas colunas do CSV. Lido sem executar macro nem fórmula; só a primeira planilha.
4. **X-4.** **Nubank conta CSV:** `Data,Valor,Identificador,Descrição`. O `Identificador` vira `external_id` (spec 06,
   I-1), então reimportar não duplica.
4a. **X-4a.** **Achado de 2026-10-19 (Nubank conta, amostra real de 01 a 16/10):** cabeçalho `Data,Valor,Identificador,
   Descrição`; data `DD/MM/AAAA`; valor com **ponto decimal e sinal** (`-5000.91`); `Identificador` é UUID; sem coluna de
   saldo. O `AmountParser` atual já lê esse valor (um só separador: ponto, 2 casas). A descrição de Pix traz nome,
   documento (CPF mascarado ou CNPJ) e banco da contraparte; "Aplicação RDB", "Pagamento de fatura" e "Pagamento de
   boleto efetuado - <favorecido>" vêm sem contraparte. Sem coluna de saldo, a reconciliação (X-6) não vem deste arquivo.
5. **X-5.** **Caixa:** formato **a levantar**. Em 2026-10-19 chegou só um **comprovante de Pix** em PDF **sem camada de
   texto** (imagem): não é extrato e não serve de amostra de leitor. Falta um extrato da conta.
   Sem extrato de exemplo o leitor não é escrito (nada de adivinhar colunas). Pergunta aberta: CSV ou OFX (o OFX já
   está no escopo do D5).
6. **X-6.** A coluna `Saldo`, quando existe, alimenta a reconciliação do D2 (spec 02): saldo confirmado = saldo da
   última linha do arquivo, com a data dela.
7. **X-7.** O registry escolhe o leitor pelo **cabeçalho/estrutura**. Dois leitores casando, ou nenhum, vira erro
   explícito para o usuário escolher; nunca cai em silêncio no CSV genérico.
8. **X-8.** Fixtures de teste são **sintéticas** (mesma estrutura, dados inventados). Extrato real não entra no Git.

9. **X-9.** **Dependência da deduplicação (achado no código de 2026-10-19):** hoje a chave é `dedupe_hash`, sem
   ordinal e dependente da conta (R2, R3); o `external_id` por conteúdo e ordinal só chega no D5 (spec 06, I-1 a I-3a).
   O extrato do Santander não traz identificador, então **depende** dessa chave. Dois caminhos, a decidir pelo
   Roberto: (a) puxar o `external_id` do D5 para antes dos leitores; (b) liberar os leitores com a chave atual e o
   risco conhecido de colapsar duas linhas idênticas no mesmo dia. A spec recomenda (a).

## Casos de teste

```ruby
# spec/services/bank_import/santander_csv_reader_spec.rb
# arquivo latin-1 com BOM e 7 linhas de cabeçalho → N linhas, acentos corretos, "-R$ 1.234,56" → -1234.56
# arquivo com separador "," → recusado com mensagem
# última linha traz Saldo 42284,06 → saldo confirmado 42.284,06 na data dela
# spec/services/bank_import/nubank_conta_csv_reader_spec.rb
# Identificador usado como external_id; reimportar o mesmo arquivo → 0 novas
# spec/services/bank_import/registry_spec.rb
# cabeçalho do Santander → leitor Santander; cabeçalho desconhecido → erro, não CSV genérico
```
