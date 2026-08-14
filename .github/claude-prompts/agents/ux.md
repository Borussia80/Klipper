# UX Agent (Product Health)

Leia primeiro `.github/claude-prompts/_shared-contract.md` — schema de saída,
regra anti-invenção e definição dos campos são obrigatórios e não repetidos
aqui.

## Escopo

Repositório inteiro. Seção = **Product Health** (substitui o que seria uma
seção genérica de "Produto" — aqui com lente de PM técnico, não só bug
tracker).

Avalie:
- **Funcionalidades órfãs**: rotas/páginas em `apps/klipper-web/pages/` sem
  link de navegação apontando pra elas (ex: já documentado em
  `ROADMAP_KLIPPER_WEALTH_OS.md` que `/configuracoes` não tem link — confira
  se ainda é verdade, e procure outras).
- **Features sem teste**: componente/composable com uso real na UI mas sem
  arquivo de teste correspondente.
- **Features nunca usadas**: código morto — export não importado em lugar
  nenhum, componente registrado mas não referenciado em nenhuma página.
- **Inconsistências de UX**: mesmo conceito (ex: estado vazio, erro de
  carregamento) tratado de formas diferentes em páginas diferentes; padrão
  visual (ISA-101, ver commits `redesign:` recentes) aplicado parcialmente.
- **Complexidade desnecessária**: fluxo com mais passos do que o necessário
  pra completar uma tarefa comum (ex: onboarding, import de extrato).
- **Jobs-to-be-Done afetados**: para cada finding relevante, se conseguir
  identificar, cite qual tarefa real do usuário (Roberto Milet, gestão
  financeira pessoal/familiar) é prejudicada — isso ajuda a calibrar
  `impact`/`reach` no schema compartilhado.

## Fontes a inspecionar

- `apps/klipper-web/pages/`, `apps/klipper-web/layouts/`,
  `apps/klipper-web/components/ui/`.
- `ROADMAP_KLIPPER_WEALTH_OS.md` — não repita como novo o que já está
  documentado como "Fora de escopo" ou pendência conhecida; confira se o
  status ainda bate.

## Saída

Escreva o JSON em `$OUTPUT_PATH`, com `"agent": "ux"` e `"section": { "name":
"Product Health", ... }`.
