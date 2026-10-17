# Spec 07 — Motor de regras de categorização e aprendizado

**Onde mora:**
- `CategorizationRule`: model.
- `RuleEngine`: service puro sobre um lançamento em memória.
- `AutoCategorizerService`: vira a fachada que chama o `RuleEngine`; a assinatura `call(description, user)` é
  mantida, porque três lugares a usam.

Segue a decisão registrada na memória do projeto: **fuzzy + regras locais, não ML**.

## Regras

1. **G-1.** Regra = condições + ações + `ativa` + `origem` (`usuario` | `aprendida` | `padrao`).
2. **G-2.** Condições (todas precisam valer; "ou" fica para depois):

| Campo | Operadores |
|---|---|
| descrição normalizada | `é`, `contém`, `começa com`, `um de` (lista) |
| valor | `é`, `aproximadamente` (±7,5 %), `entre`, `maior que`, `menor que` |
| conta | `é`, `um de` |
| tipo | `débito`, `crédito` |

3. **G-3.** Ações: definir categoria, definir `kind` (spec 03), definir portador (`member`), renomear descrição.
4. **G-4.** **Ordem: da mais específica para a menos**, como no Actual (`rule-utils.ts`). Pontos por operador: `é` 10,
   `um de` 9, `aproximadamente`/`entre` 5, comparação 1, `contém`/`começa com` 0. Regra só com igualdades vale o
   dobro. Empate → a mais nova primeiro (o usuário corrigiu por último). A ordem é determinística.
5. **G-5.** Para cada campo, **a primeira regra que define o campo ganha**; as seguintes não o sobrescrevem, mas
   podem definir outros campos.
6. **G-6.** Regra do usuário sempre antes de regra `padrao` com a mesma pontuação.
7. **G-7.** As 8 regex atuais viram regras `padrao` semeadas (o `DefaultCategoriesSeederService` já semeia
   categorias), exceto a de "Renda": `/pagamento/` sai (ver spec 03, L-12 e R1).
8. **G-8.** Regra só é aplicada a lançamento **novo** (criação manual sem categoria e importação). Reaplicar a lançamentos
   existentes é uma ação explícita ("aplicar às N transações que casam"), com pré-visualização.
9. **G-9.** Mesclar categoria (Fatia 1 de UX): regras que apontam para a origem passam a apontar para o destino.

## Aprendizado com correções

10. **G-10.** Quando o usuário **muda a categoria** de um lançamento, olha-se os **5 mais recentes** com a mesma
    descrição normalizada. Se uma categoria aparece **3 ou mais vezes** entre eles, cria (ou atualiza) a regra
    `aprendida` "descrição é X → categoria Y". (Limiares do Actual, `getProbableCategory`.)
11. **G-11.** Regra aprendida não sobrescreve regra do usuário para a mesma descrição; se houver, nada é criado.
12. **G-12.** O usuário vê e apaga regras aprendidas em `/configuracoes`. Apagada, não volta a ser aprendida para a
    mesma descrição e categoria (`rejeitada: true`).

## Casos de teste (RSpec)

```ruby
# spec/services/rule_engine_spec.rb
# "UBER *TRIP" com regra padrão contém "uber" → Transporte
# regra usuário descrição é "uber *trip" → Lazer  ⇒ Lazer (é > contém)
# duas regras "contém" empatadas → a mais nova ganha
# regra A define categoria, regra B (menos específica) define categoria e portador → categoria de A, portador de B
# valor aproximadamente 100: 92.50 casa, 107.50 casa, 107.51 não casa
# "Pagamento em 10 JUN" → sem categoria (G-7)
# regra inativa é ignorada

# spec/services/category_learning_spec.rb
# 3 correções "PADARIA DO ZE" → Alimentação em 5 recentes → cria regra aprendida
# 2 correções → não cria
# regra do usuário existente para a descrição → não cria aprendida
# regra aprendida apagada → 3 novas correções não recriam
```
