# 04 — Tokens do Klipper

**Direção visual:** náutica — azul-marinho profundo + latão, todo dado dentro de card com moldura visível.
**Fonte de verdade:** `apps/klipper-web/assets/css/tokens.css` e `docs/design/klipper_mockup.html`.
**Decisão de 2026-10-17:** a paleta **não muda**. Nada de Sure, Cashew ou ezBookkeeping entra como valor visual;
das referências o Klipper leva fluxo e funcionalidade (ver `03-matriz-referencias.md`).

Este documento existe para as specs de `05-specs/` usarem os nomes certos.

## 1. Regra de cor (a do `tokens.css`)

Cor aparece só em:

1. o **instrumento primário** da tela (`--ok`, um por página);
2. **condições anormais** que pedem ação (`--warn`, `--alert`);
3. **elementos interativos** (`--sea`: botão, link, foco);
4. **marca**, CTA principal e item ativo da navegação (`--brass`);
5. **paleta categórica fixa** em gráficos de composição (split fixo/cartão/variável, ranking de dívida);
6. **identidade de banco** em listas (`--bank-*`) — mantida por decisão de 2026-10-17.

Todo o resto é escala neutra (`--t1`…`--t4`), com hierarquia por tamanho e posição. Toda superfície de dado vive
num card com `--bd`/`--bd-hi`. Condição anormal sempre com **ícone + texto**, nunca só cor.

## 2. Cores e contraste (WCAG 2.x, calculado)

| Token | Valor | Uso | sobre `--bg` | sobre `--sf` | sobre `--sf-hi` |
|---|---|---|---|---|---|
| `--bg` | `#0A0F1A` | canvas | — | — | — |
| `--bg-frame` | `#070B12` | navegação e topbar | — | — | — |
| `--sf` | `#111A28` | card | — | — | — |
| `--sf-hi` | `#16212F` | card elevado, hover | — | — | — |
| `--ly2` | `#1D2C3D` | camada 2 | — | — | — |
| `--bd` / `--bd-hi` | `#223145` / `#2E4059` | moldura do card | — | — | — |
| `--t1` | `#EEF3F9` | número, texto primário | 17,2 | 15,7 | 14,6 |
| `--t2` | `#9FB0C3` | texto secundário | 8,6 | 7,9 | 7,3 |
| `--t3` | `#8393A4` | auxiliar — **piso para texto** | 6,1 | 5,6 | 5,2 |
| `--t4` | `#4A5A70` | **nunca texto**; borda, trilho, grade de gráfico | 2,7 | 2,5 | 2,3 |
| `--sea` | `#3BB8C4` | interativo (+ `--blt` tint, `--bdm` wash) | 8,1 | 7,4 | 6,8 |
| `--ok` | `#43C59E` | instrumento primário, confirmação (+ `--okd`) | 8,9 | 8,1 | 7,5 |
| `--warn` | `#E6B44C` | atenção — ação em breve (+ `--wnd`) | 10,0 | 9,2 | 8,5 |
| `--alert` | `#E8735A` | anormal — ação agora (+ `--ald`) | 6,4 | 5,9 | 5,4 |
| `--brass` | `#D9A85C` | marca, CTA, item ativo (+ `--brass-dim`) | 8,9 | 8,1 | 7,5 |
| `--bank-nubank/itau/btg` | — | identidade de banco | — | — | — |

Todos os pares de texto passam AA (≥ 4,5:1), exceto `--t4`, que não é texto.

### Prioridade das condições anormais nas specs

| Prioridade | Token | Exemplo |
|---|---|---|
| Ação agora | `--alert` + `--ald` | saldo negativo; fatura vencida; orçamento > 100 % |
| Ação em breve | `--warn` + `--wnd` | fatura vence em ≤ 3 dias; saldo previsto negativo |
| Vale olhar | sem cor: `--t1` + borda `--bd-hi` + ícone | gasto acima do ritmo do mês; dado desatualizado |

"Vale olhar" fica sem cor própria porque um terceiro amarelo ficaria indistinguível de `--warn` no celular.

## 3. Forma

| Token | Valor |
|---|---|
| `--r` | 14 px (card, botão) |
| `--r-sm` | 9 px (chip, campo) |
| `--nav` | 232 px (barra lateral) |

## 4. Tipografia

**Inter** (corpo, rótulos) e **Space Grotesk** (números, títulos), via `@nuxt/fonts` → Google Fonts, OFL-1.1.
Número monetário com `.mono` (`tabular-nums`). Não há escala tipográfica em token — tamanhos ficam nos componentes,
seguindo o `klipper_mockup.html`.

## 5. O que as specs acrescentam sem mexer na paleta

- **Alvo de toque mínimo de 44 px** no mobile (folha de lançamento, gestos da lista).
- **Breakpoint de troca mobile/desktop: 768 px** (o mesmo que a navegação já usa).
- **Largura do conteúdo:** `main.css` limita `.shell-main > *` a 760 px e o painel sobrescreve para 1160 px
  inline. As specs do painel e de transações pedem mais espaço em 1440 px; a mudança do limite fica para o PR da
  fatia que precisar, com screenshot antes/depois.
- **Sem animação de contagem em número:** atrasa a leitura. (`composables/useCountUp.ts` existe mas não é usado —
  dead code pré-existente, só registrado.)
- **Ícones:** Phosphor (MIT), já centralizado em `components/ui/AppIcon.vue`.
