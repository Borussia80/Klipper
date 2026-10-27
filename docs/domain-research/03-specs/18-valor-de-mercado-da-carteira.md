# Spec 18 — Valor de mercado da carteira

**Status:** rascunho. **Origem:** backlog de 18/10, item 14 (P2), diferença de cotação entre agregador e corretora
para FIIs. **Estende:** D9 e spec 02, C-15.
**Onde mora:** `position_valuations` (posição, data, valor), `StockQuoteService` (cotação de ações) e a tela de
patrimônio/posição.

## Regras

1. **V-1.** Valor manual de posição e cotação são fontes distintas; a tela informa qual delas formou o valor exibido.
2. **V-2.** Todo valor de posição exibe sempre a data e a fonte: manual, agregador, corretora ou cotação obtida pelo
   `StockQuoteService`, quando aplicável.
3. **V-3.** Custo e valor de mercado nunca aparecem misturados sem rótulo. Sem valor de mercado, o investimento usa
   custo e o rótulo “custo”, conforme C-15.
4. **V-4.** Havendo valor de mercado, o patrimônio usa esse valor; a atualização manual é registrada em
   `position_valuations` com posição, data e valor.
5. **V-5.** A diferença entre o valor do agregador e o da corretora usa tolerância configurável. Ultrapassada a
   tolerância, o sistema mostra alerta de divergência, com as duas fontes e respectivas datas.
6. **V-6.** O alerta não escolhe silenciosamente uma fonte nem regrava valor manual; a escolha ou correção permanece
   explícita ao usuário.
7. **V-7.** A divergência para FIIs entra no mesmo tratamento de fontes e alerta; esta spec não presume a causa da
   diferença.
8. **V-8.** Ficam fora deste item: fórmula de rentabilidade, cálculo de CDI/IPCA, obtenção de novas cotações e
   reconciliação automática entre agregador e corretora.

## Casos de teste

```ruby
# valor manual de posição → tela mostra valor, data e fonte manual
# sem valor de mercado → patrimônio usa custo com rótulo "custo"
# agregador e corretora dentro da tolerância configurada → sem alerta
# agregador e corretora além da tolerância → alerta com ambas as fontes e datas
# alerta de divergência → não altera automaticamente o valor manual
```

## Critérios de pronto

- Valor, data e fonte aparecem juntos em cada valor usado pela posição.
- Custo e mercado têm rótulos distintos.
- A tolerância é configurável e a divergência acima dela é visível, sem escolha automática.
- Os casos de teste cobrem custo, valor manual e divergência entre fontes.

## Perguntas abertas

- Onde será configurada a tolerância e ela será única ou por posição?
- Como a tela apresenta fontes com datas diferentes sem sugerir equivalência entre elas?
- Qual ação do usuário confirma a fonte a usar após um alerta de divergência?
