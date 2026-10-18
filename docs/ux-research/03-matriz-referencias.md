# 03 — Matriz de referências

Legenda das fontes: **S** = Sure (visual, sala limpa) · **C** = Cashew (fluxo mobile, sala limpa) ·
**E** = ezBookkeeping (estrutura, MIT). Itens de S e C marcados *[a observar]* dependem da sessão de observação
(ver inventários); a decisão de design não espera por eles, mas pode ser ajustada depois.

## Regras de cor do Klipper que arbitram os conflitos

Vêm do `tokens.css` (detalhe em `04-design-tokens.md`); a direção é a náutica, sem mudança de paleta.

1. **Cor só onde significa algo:** instrumento primário da tela, condição anormal, elemento interativo, marca,
   paleta categórica de gráficos de composição e identidade de banco. O resto é escala neutra.
2. **Condição anormal por prioridade**, não por "positivo/negativo": ação agora (`--alert`), ação em breve
   (`--warn`), vale olhar (neutro + ícone). Variação mensal positiva não é verde — é texto neutro com sinal.
3. **Redundância:** cor nunca sozinha; sempre ícone + texto (daltonismo, luz solar no celular).
4. **Moldura e hierarquia:** todo dado dentro de card com borda visível, número dominante grande, contexto pequeno.
5. **Layout estável:** blocos não mudam de lugar entre visitas; o que some é bloco sem dado, nunca reordenado.

## Matriz

| Tela do Klipper | Visual | Fluxo / interação | Estrutura / funcionalidade | Levar | Descartar | Regra de cor → resolução | Existe hoje? |
|---|---|---|---|---|---|---|---|
| **Painel (desktop)** | S1 | — | E6 (só ocultar bloco) | S: patrimônio como número-herói, gráfico de evolução logo abaixo, blocos com muito ar. E: usuário poder ocultar bloco | S: assistente de IA ao lado. E: reordenar blocos livremente | Gráficos de S tendem a colorir ganho/perda → linha neutra; só o trecho abaixo de zero ganha `--alert` | **Parcial** — painel atual é do *mês*, não do *patrimônio*; tem os blocos de mês |
| **Painel (mobile)** | S1 (densidade reduzida) | C2 (nav inferior + "+") | — | C: resumo curto no topo, lista dos últimos lançamentos, "+" sempre visível | C: cartões coloridos por conta | Uma cor por conta conflita → conta identificada por nome + ícone neutro | **Parcial** |
| **Lançamento rápido** | — | **C1** | **E5** (expressão no valor), E1 (seletor de categoria em dois níveis) | C: valor primeiro, teclado numérico, categoria em grade, data = hoje, salvar em ≤ 4 toques. E: `45,90+12` | C: cor por categoria na grade | Grade de ícones coloridos → ícones neutros; destaque só no selecionado (borda `--sea`) | **Parcial** — `ModalNovoLancamento` é formulário genérico |
| **Transações** | S4 | C4 (arrastar com desfazer; toque longo = lote) | E: filtros por categoria pai/filha | S: densidade de tabela no desktop. C: gestos no mobile. E: filtro em árvore | C: apagar sem desfazer (se for o caso) | Valor de entrada em verde por padrão → sinal + texto neutro; cor só para estorno/anomalia | **Sim** (falta gesto, filtro por categoria, filtro por conta) |
| **Contas** | S2 | — | — | S: agrupar por tipo com subtotal; conta desatualizada sinalizada | S: logos coloridos grandes | Cor de banco (`--bank-*`) **mantida** (decisão de 2026-10-17), restrita ao ícone pequeno da linha; nunca em valor ou fundo | **Parcial** — lista plana |
| **Detalhe de conta** | S3 | — | — | S: gráfico de saldo da conta + transações da conta abaixo | — | Área preenchida colorida → linha neutra, zero marcado, saldo negativo em `--alert` | **Não** |
| **Orçamento** | S5 | **C3** | E1 (limite na categoria pai soma filhas) | C: "quanto posso gastar por dia", marcador do ponto ideal do mês. E: orçamento por categoria pai | C: período personalizado (viagem) — fica para depois; C: metas de poupança | Barra verde/amarela/vermelha permanente → barra neutra; cor só quando o gasto passa do limite (`--alert`); acima do ritmo = "vale olhar" (neutro + ícone) | **Sim** (falta ritmo diário e marcador) |
| **Categorias** | — | C6 (sugestão por título) | **E1** | E: dois níveis fixos, ordem, ocultar. C: título → categoria | E: categoria de transferência como entidade separada | Cor por categoria é necessária em gráficos de composição → paleta categórica fixa, usada **só** em gráficos de composição | **Parcial** — um nível; `AutoCategorizerService` já faz título → categoria |
| **Agendadas / recorrentes** | — | C5 | **E2** | E: template com frequência, início/fim, geração automática. C: lista por próximo vencimento | E: execução a cada 15 min (o Klipper roda no Render Free, que hiberna) | Vencimento próximo é condição anormal legítima → `--warn` quando vence em ≤ 3 dias sem saldo previsto | **Não** |
| **Importação** | S6 | — | **E3**, **E4** (OFX) | E: regras condição → ação na prévia; OFX genérico | E: formatos chineses, Camt, MT940 | Prévia com linhas coloridas por status → neutras; só duplicata e erro marcados | **Sim** (falta OFX e regras editáveis) |
| **Relatórios** | S1/S3 | — | — | S: gráficos sóbrios, eixo limpo | — | Paleta categórica fixa do `tokens.css` | **Sim** |
| **Configurações** | S7 | — | **E7** | E: seções (perfil, preferências de exibição, dados, sessão) | E: 2FA, OIDC, câmbio, i18n | — | **Parcial** — tokens quebrados (bug conhecido) |
| **Investimentos** | S1 | — | — | S: posição + evolução | — | Rentabilidade em verde/vermelho → neutro com sinal; `--alert` só para perda acima de limite definido | **Sim** |
| **Portadores** | — | — | — | — | — | — | **Sim** (sem referência nos três apps) |
| **Kakebo** | — | — | — | Nenhum dos três tem; spec própria em `docs/KAKEBO.md` | — | — | **Não** (fora desta pesquisa) |

## Desktop × mobile: a regra que o Klipper adota

Do ezBookkeeping leva-se o **princípio**, não as duas árvores: uma rota por tela, lógica em composables, e
componente de apresentação mobile separado **só** onde a interação muda — lançamento rápido (folha inferior com
teclado), lista de transações (gestos) e navegação (inferior vs. lateral). Breakpoint único de troca: 768 px.
