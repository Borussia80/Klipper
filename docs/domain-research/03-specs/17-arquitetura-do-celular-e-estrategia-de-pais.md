# Spec 17 — Arquitetura do celular e estratégia de país

**Status:** rascunho. **Origem:** decisão para Android/iOS e intenção futura de gerar renda.
**Onde mora:** clientes Android/iOS via Capacitor; o núcleo atual e a API própria permanecem referência de negócio.

## Regras

1. **A-1.** A opção A é app nativo com Capacitor falando com a API própria do usuário e Postgres no computador ou
   servidor de casa: custo baixo e privacidade alta.
2. **A-2.** A opção B é local-first: SQLite criptografado com SQLCipher por plugin Capacitor. Dá privacidade total,
   mas custa mais porque exige portar para TypeScript a lógica hoje em Ruby, inclusive importadores de PDF,
   `ExternalId`, `OwnTransferMatcher`, calculators e orçamento.
3. **A-3.** A opção C é híbrida: banco no aparelho e sincronização opcional com servidor próprio.
4. **A-4.** MariaDB fica descartado: é servidor, não tem índice parcial nativo e não traz ganho identificado.
5. **A-5.** DuckDB só pode ser camada de análise: é OLAP embutido, não é adequado à escrita transacional e não há
   adapter Rails oficial.
6. **A-6.** CSV serve exclusivamente para exportar, backup ou importar; nunca é banco, pois não fornece integridade,
   consultas ou atomicidade e é texto puro.
7. **A-7.** SQLite com SQLCipher é a recomendação para dados locais. Fontes secundárias, não verificadas no código,
   dizem que Cashew usa SQLite via Drift com backup/sincronização opcional por Firebase/Google Drive.
8. **A-8.** PGlite (Postgres em WebAssembly) é candidato a avaliar, não decisão: verificar persistência em IndexedDB
   que o sistema possa limpar, memória e abertura em celular fraco, criptografia em repouso e maturidade.
9. **A-9.** Wallet by BudgetBakers é tratado como modelo nuvem-primeiro, segundo fontes secundárias.
10. **A-10.** A prova de conceito roda, com dados sintéticos, SQLite criptografado e PGlite: a migration de
    `external_id` e uma importação. A decisão registra se ambos completam esses casos e os riscos de A-8.
11. **A-11.** Brasil é o primeiro país. Pacotes de país reúnem importadores, calendário de feriados, tabelas legais
    em dados versionados, idioma e categorias, sobre um único núcleo.
12. **A-12.** O preço nas lojas é regional. Agregação bancária é escolha de produto e conflita com “nada sai do
    aparelho”; se existir, deve ser decisão explícita.
13. **A-13.** O segundo país só é escolhido com critérios registrados: necessidade de novo pacote de país, suporte aos
    importadores, impacto legal/tributário e compatibilidade com o núcleo único.
14. **A-14.** Cuidados jurídicos e tributários exigem validação apropriada; esta spec não é aconselhamento jurídico ou
    tributário.
15. **A-15.** O diferencial brasileiro é a leitura de extratos dos bancos brasileiros e regras brasileiras: Pix
    próprio, fatura e parcelas.

## Casos de decisão

```text
SQLite+SQLCipher: migration external_id + importação sintética concluem → apto para dados locais.
PGlite: mesmos casos concluem e riscos A-8 são aceitos → permanece candidato; caso contrário, não é escolhido.
CSV em escrita transacional → recusado como banco.
Agregação bancária proposta → explicitar a exceção a “nada sai do aparelho” antes de implementar.
```

## Critérios de pronto

- A prova de conceito registra resultado dos dois bancos e dos dados sintéticos.
- A decisão identifica a opção A, B ou C e os riscos aceitos.
- O pacote Brasil especifica seus dados versionados e o núcleo não recebe regra exclusiva sem pacote.
- A escolha do segundo país usa os critérios A-13 e a revisão aplicável foi identificada.

## Perguntas abertas

- Qual opção, A, B ou C, atende primeiro à renda futura sem abandonar a privacidade desejada?
- PGlite preserva dados e desempenho aceitáveis no aparelho, inclusive em criptografia em repouso?
- Quais critérios terão peso decisivo para selecionar o segundo país?
