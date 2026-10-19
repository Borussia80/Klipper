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
3. **X-3.** **Santander xlsx:** mesmas colunas do CSV. Lido sem executar macro nem fórmula; só a primeira planilha.
4. **X-4.** **Nubank conta CSV:** `Data,Valor,Identificador,Descrição`. O `Identificador` vira `external_id` (spec 06,
   I-1), então reimportar não duplica.
5. **X-5.** **Caixa:** formato **a levantar**. Não há extrato de exemplo; sem ele o leitor não é escrito (nada de
   adivinhar colunas). Pergunta aberta: CSV ou OFX (o OFX já está no escopo do D5).
6. **X-6.** A coluna `Saldo`, quando existe, alimenta a reconciliação do D2 (spec 02): saldo confirmado = saldo da
   última linha do arquivo, com a data dela.
7. **X-7.** O registry escolhe o leitor pelo **cabeçalho/estrutura**. Dois leitores casando, ou nenhum, vira erro
   explícito para o usuário escolher; nunca cai em silêncio no CSV genérico.
8. **X-8.** Fixtures de teste são **sintéticas** (mesma estrutura, dados inventados). Extrato real não entra no Git.

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
