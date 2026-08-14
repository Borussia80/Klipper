# Roadmap de Redesign Visual — Klipper

**Gerado em:** 2026-07-10
**Substitui:** a direção "HMI ISA-101" (rejeitada — resultou em telas vazias, números sem moldura, aparência de rascunho).
**Direção nova aprovada:** náutica premium — azul-marinho profundo + accent de latão/bronze, todo dado dentro de card com moldura clara.
**Referência visual canônica:** `klipper_mockup.html` (anexo). Este arquivo NÃO é inspiração solta — é a especificação. O resultado tem que ser reconhecível como o mesmo produto do mockup.

---

## Por que este roadmap é diferente (leia antes de abrir o Claude Code)

O redesign anterior falhou porque a spec era prosa ("racionalização de cor", "instrumento primário") e o Claude Code preencheu as lacunas com as próprias suposições — que deram errado. A correção não é escrever mais prosa; é trocar prosa por três coisas que não deixam margem:

1. **Um mockup HTML como fonte de verdade.** Sempre que a instrução e o mockup divergirem, o mockup vence. Diga isso explicitamente a cada sessão: *"o `klipper_mockup.html` é a spec; onde tiver dúvida, reproduza o mockup, não improvise."*
2. **Critério de aceite verificável por imagem, não por descrição.** Cada item abaixo termina em "pronto quando o screenshot mostra X" — algo que se confirma olhando, não lendo. Peça ao Claude Code para tirar screenshot e comparar com o mockup antes de dizer que terminou.
3. **Uma tela por sessão.** O erro clássico é pedir "aplica o redesign no app" e receber 13 telas meia-boca. Faça `/dashboard` ficar idêntico ao mockup primeiro. Só depois propague.

Regras que já funcionaram nas sessões de backend e continuam valendo: pedir o plano antes do código; não tocar no que não foi pedido; rodar os testes (Vitest) depois de cada mudança; revisar o diff.

---

## Fatia 0 — Fundação de tokens e tipografia

**Objetivo:** trocar a base visual inteira sem ainda reconstruir telas.

**Escopo:**
- Reescrever `assets/css/tokens.css` com a paleta do mockup (copiar os valores hex do `:root` do `klipper_mockup.html` — são a fonte). Manter os MESMOS nomes de variáveis já usados no projeto para herança automática.
- Fontes: `Space Grotesk` (display, números, títulos) + `Inter` (corpo, labels). Configurar via `nuxt.config.ts`.
- NÃO reconstruir nenhuma página nesta fatia — só a base.

**Pronto quando:** abrir qualquer tela existente e o fundo estar azul-marinho profundo (não grafite, não o azul-preto antigo), os números em Space Grotesk, e nenhuma cor roxa (`--pur`) restar em lugar nenhum.

---

## Fatia 1 — Dashboard idêntico ao mockup

**Objetivo:** `/dashboard` tem que ficar visualmente igual ao `klipper_mockup.html`.

**Escopo — componentes na ordem do mockup:**
1. **Hero com faceplate** — card de resultado do mês com borda visível, fundo em gradiente sutil, número grande em Space Grotesk, barra de faixa real com escala embaixo. NÃO é número solto no vazio (esse foi o erro anterior).
2. **Alarme acionável** — faixa coral com ícone, texto e botão de ação. Só aparece quando há condição real (ex: fatura vencendo, orçamento estourado). Zero alarmes = a faixa some (não vira texto cinza solto).
3. **Grid de 3 KPIs** — salário / fixos / cartões, cada um em card com moldura, ícone no canto, chip de status quando relevante.
4. **Duas colunas** — "Fixo × Cartão × Variável" (barras) e "Prioridade de quitação" (lista ranqueada de cartões), cada uma em card.
5. **Card de reembolso** — cobertura Bradesco das terapias, com barra de gasto vs. reembolsado.

**Dados:** todos reais, vindos da API. Onde não houver endpoint, ocultar o bloco — nunca inventar valor (o dado fake foi o outro problema que você já apontou).

**Pronto quando:** screenshot de `/dashboard` lado a lado com o mockup — um leigo não consegue dizer qual é qual. Cada número está dentro de um card com borda visível. Nenhum elemento flutua sem moldura.

---

## Fatia 2 — Propagar para as telas de dado (Movimento, Orçamento, Cartões)

**Objetivo:** as três telas mais usadas ganham o mesmo tratamento de card do dashboard.

**Escopo:**
- `/transacoes` (Movimento): lista em cards agrupados por data, não linhas soltas.
- `/orcamento`: os cards Alocado/Gasto/Livre no padrão do mockup; envelopes de categoria em cards com moldura.
- `/contas` (Cartões): cada cartão em card definido; a seção "prioridade de quitação" reaproveita o componente da Fatia 1.
- **Corrigir aqui** o bug já detectado: na tela de orçamento, o cabeçalho diz "Julho 2026" mas o seletor mostra "Junho 2026" — header e dropdown lendo fontes diferentes. Resolver junto, já que estamos nesta tela.

**Pronto quando:** navegar dashboard → movimento → orçamento → cartões sem nenhuma "quebra" visual — todas parecem o mesmo produto, todas com cards de moldura clara. E o mês do header bate com o seletor.

---

## Fatia 3 — Telas secundárias e modais

**Objetivo:** fechar a consistência no resto.

**Escopo:**
- Investimentos, Portadores, Relatórios, Kira, Importar: herdam tokens (já vêm coesas da Fatia 0) + ganham estrutura de card onde ainda estiver solto.
- Modais (drawer): manter a mecânica atual (focus trap, ARIA — já funciona), trocar só a pele para o padrão do mockup. Remover a stripe azul decorativa do topo.
- Estado vazio de cada tela: uma frase que convida à ação ("Nenhum lançamento ainda — importe um extrato para começar"), não um vazio morto.

**Pronto quando:** todas as 13 rotas abrem sem nenhuma tela destoando das outras, e nenhum modal tem visual diferente do padrão.

---

## Fora de escopo (não fazer agora, registrar para depois)

- Tema claro — a direção é dark-first; tema claro é projeto separado, não misturar aqui.
- Animações elaboradas — micro-transições de hover já bastam; evitar excesso (é o que faz parecer "gerado por IA").
- Reescrever a lógica de negócio — este roadmap é 100% visual/apresentação; nenhuma mudança de cálculo, endpoint ou schema.

---

## Checklist de verificação (rodar ao fim de cada fatia)

- [ ] Screenshot da tela comparado com `klipper_mockup.html` — reconhecível como o mesmo produto?
- [ ] Todo número está dentro de um card com borda visível (nada flutuando)?
- [ ] Cor semântica (verde/âmbar/coral) só aparece onde há significado, nunca em elemento decorativo?
- [ ] Nenhum dado fake/hardcoded restou (grep pelos valores do mockup no código)?
- [ ] `npm run test` (Vitest) verde?
- [ ] Responsivo: em tela estreita, o grid vira 1 coluna sem quebrar?
- [ ] Foco de teclado visível e `prefers-reduced-motion` respeitado?

---

*Referência visual: `klipper_mockup.html`. Onde a prosa deste roadmap e o mockup divergirem, o mockup é a fonte de verdade.*
