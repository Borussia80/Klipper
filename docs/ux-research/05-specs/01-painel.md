# Spec 01 — Painel

**Rota:** `/dashboard` · **Prioridade:** 1 · **Referências:** visual S1, mobile C2, ocultar bloco E6.
Implementável sem abrir nenhuma referência.

## Objetivo

Responder em 3 segundos, nesta ordem: (1) quanto eu tenho, (2) tem algo pedindo ação, (3) como está o mês.
Hoje o painel responde só (3) e (2); o patrimônio está escondido em `/relatorios`.

## Layout desktop (≥ 1200 px, conteúdo até 1280 px, 12 colunas)

```
┌──────────────────────────────────────────────┬──────────────────────┐
│ PATRIMÔNIO LÍQUIDO              [6m 1a Tudo] │ ALARMES (0–3 faixas) │
│ R$ 184.320,55   (hero)                        │  ou "Nada pedindo    │
│ +R$ 2.140 desde mês passado (neutro, c/ sinal)│   ação agora."       │
│ ───── gráfico de linha do patrimônio ─────── │                      │
├───────────────┬───────────────┬──────────────┴──────────────────────┤
│ Em contas     │ Investido     │ Cartões a pagar                     │
├───────────────┴───────────────┴─────────────────────────────────────┤
│ RESULTADO DO MÊS (InstrumentReadout atual) + barra do mês decorrido │
├──────────────────────────────────┬──────────────────────────────────┤
│ Fixo × Cartão × Variável         │ Prioridade de quitação           │
├──────────────────────────────────┴──────────────────────────────────┤
│ Últimos lançamentos (5)                               Ver todos →   │
└─────────────────────────────────────────────────────────────────────┘
```
Colunas: herói 8, alarmes 4; KPIs 4+4+4; mês 12; composição 6+6; lista 12.
Entre 768 e 1199 px: alarmes descem para baixo do herói, KPIs em 3 colunas, composição empilha.

## Layout mobile (< 768 px)

Ordem: alarmes (só se houver) → herói (32 px) com gráfico de 120 px de altura → 3 KPIs em lista (rótulo à esquerda,
valor à direita, sem cards lado a lado) → resultado do mês → últimos 5 lançamentos. Composição e quitação ficam
recolhidas sob "Mais detalhes do mês". Navegação inferior com "+" central (spec 02).

## Dados (API existente)

| Bloco | Endpoint | Campo |
|---|---|---|
| Herói | `GET /reports/net_worth` | `net_worth` |
| Variação | `GET /reports/net_worth_history` | penúltimo ponto vs. `net_worth` atual |
| Gráfico | `GET /reports/net_worth_history?period=6m\|1a\|max` | `points[]` — já existe (`PERIOD_MONTHS` aceita `3m`, `6m`, `1a`; omitir = tudo) |
| Em contas / Investido | `net_worth` | `accounts_total`, `investments_cost` |
| Cartões a pagar | `GET /accounts` | soma de `saldo_fatura_atual` das contas tipo cartão |
| Alarmes | `debt_ranking`, `budgets/summary`, `data_health`, `accounts` | ver regras abaixo |
| Mês, composição, quitação | já consumidos hoje | — |
| Últimos lançamentos | `GET /transactions?per_page=5` | — |

## Regras de alarme (máximo 3 faixas visíveis, ordenadas por prioridade)

Prioridades: **Crítico** = ação agora (`--alert` + `--ald`) · **Alto** = ação em breve (`--warn` + `--wnd`) ·
**Aviso** = vale olhar (neutro `--t1` + borda `--bd-hi` + ícone). Ver `04-design-tokens.md` §2.

| Condição | Prioridade | Texto |
|---|---|---|
| Conta corrente com `balance < 0` | Crítico | "{conta} está negativa em {valor}." · Ação: "Ver conta" |
| Orçamento com `pct_used > 100` | Crítico | "{categoria} passou {valor} do limite do mês." · "Ver orçamento" |
| Fatura vence em ≤ 3 dias | Alto | "Fatura do {cartão} vence {dia}: {valor}." · "Ver cartão" — **requer `dia_fechamento` e `dia_vencimento`** (fatia 3, regras de calendário no plano) |
| Orçamento acima do ritmo (spec 05) | Aviso | "{categoria} está gastando mais rápido que o mês." |
| `data_health.uncategorized > 0` ou `without_account > 0` | Aviso | já existe (`DataHealthBanner`) — passa a ser faixa desta coluna |

Mais de 3: terceira faixa vira "+{n} outros avisos" que expande.

## Estados

| Estado | Comportamento |
|---|---|
| Carregando | Esqueleto com a **mesma geometria** do conteúdo (herói, 3 KPIs, mês) — nada pula ao carregar |
| Vazio (sem contas) | Herói substituído por: "Comece cadastrando onde seu dinheiro está." + [Adicionar conta] [Importar extrato]. Mantém `FirstSteps` |
| Sem histórico (1 snapshot) | Gráfico some; abaixo do herói: "O gráfico aparece a partir do segundo mês." |
| Erro parcial | Cada bloco falha sozinho: "Não deu para carregar este bloco." + [Tentar de novo]. Um endpoint fora não derruba o painel |
| Servidor acordando | `ServerWakingNotice` atual |
| Normal sem alarme | Coluna de alarmes mostra uma linha neutra: "Nada pedindo ação agora." (sem verde) |

## Interações

- Seletor de período do gráfico: 3 opções em segmento; padrão 6 meses; lembrado por `localStorage` (try/catch).
- Passar o cursor/tocar no gráfico mostra mês e valor numa etiqueta; linha vertical fina `--t4`.
- Cada KPI e cada faixa de alarme é link para a tela de origem.
- Filtro por portador (existente) continua no cabeçalho; afeta só blocos do mês.

## Visual (tokens de `04-design-tokens.md`)

Herói Space Grotesk 40 px `--t1`; variação 14 px `--t2` com sinal "+"/"−" (nunca verde/vermelho). Linha do
gráfico `--t2` 1,5 px; área abaixo de zero `--ald`; grade `--t4`. Painéis `--sf` + `--bd`.

## Critérios de aceite

1. Em 1440 px, patrimônio é o maior número da tela e está acima da dobra.
2. Com tudo normal, a única cor diferente de neutro na tela é a de ação (botões/links) e o marcador da navegação.
3. Saldo negativo numa conta produz faixa crítica com ícone + texto + botão; removendo a condição, a faixa some.
4. Derrubar `/reports/net_worth` deixa o resto do painel funcionando.
5. Em 390 px, nenhum scroll horizontal; KPIs em lista; "+" visível.
6. Teste Vitest por regra de alarme (condição → texto e prioridade).
