# Método Kakebo no Klipper

**Tipo:** feature de produto
**Status:** especificada — implementação pendente

O Kakebo é o ciclo mensal de consciência financeira do Klipper. Ele complementa
o orçamento detalhado com intenção, classificação e reflexão sobre o mês.

## Ciclo mensal

### Abertura

No início do mês, a pessoa informa a receita esperada, as despesas fixas previstas
e uma meta de economia. O sistema calcula o disponível para gastos variáveis.

### Quatro pilares

Cada despesa deve pertencer a exatamente um pilar, ou ficar explicitamente pendente:

| Pilar | Uso | Exemplos |
|---|---|---|
| **Sobrevivência** | Essencial para viver e manter a casa | alimentação, moradia, saúde, transporte necessário |
| **Lazer/Cultura** | Repertório, descanso e experiências | livros, cinema, viagens, cursos |
| **Opcionais** | Desejos que poderiam ser adiados | compras não essenciais, upgrades, conveniências |
| **Extras** | Imprevistos e despesas fora do padrão | consertos, multas, presentes, emergências |

O pilar é complementar à `natureza` existente (`fixo`, `cartao_parcelamento`,
`variavel`) e deve poder ser corrigido manualmente.

### Acompanhamento

`/kakebo` deve mostrar receita, fixos, meta, disponível, total e percentual por
pilar, quanto falta para a meta e os lançamentos ainda sem classificação.

### Fechamento

O fechamento mensal exige quatro respostas antes de ser concluído:

1. Quanto dinheiro consegui economizar?
2. Quanto pretendia economizar?
3. Em que gastei mais do que esperava e por quê?
4. Como posso melhorar no próximo mês?

O fechamento permanece editável e entra no histórico do mês.

## Escopo técnico e aceite

- Rails: ciclo mensal, abertura, pilar no lançamento e fechamento reflexivo,
  sempre isolados pelo usuário autenticado.
- API: endpoints para abrir, consultar, fechar e resumir por pilar.
- Nuxt: página `/kakebo`, navegação e Command Palette.
- RSpec e Vitest cobrindo isolamento, agregações, estados da tela e respostas
  obrigatórias.
- Não usar `localStorage` para dados financeiros ou respostas de fechamento.
