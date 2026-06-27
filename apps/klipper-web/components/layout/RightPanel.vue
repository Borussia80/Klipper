<template>
  <aside style="border-left:1px solid var(--bd);overflow-y:auto;background:var(--bg-frame);display:flex;flex-direction:column">

    <!-- ═══ DASHBOARD PANEL ═══ -->
    <template v-if="isDashboard">
      <div class="pb">
        <div class="plbl">Patrimônio total</div>
        <div class="mono" style="font-size:30px;font-weight:200;letter-spacing:-.04em;color:var(--t1);line-height:1;margin-bottom:5px">R$ 192.220</div>
        <div style="display:flex;align-items:center;gap:6px">
          <span style="font-size:12px;color:var(--ok)">▲ +R$ 5.320</span>
          <span style="font-size:11px;color:var(--t4)">este mês (+2,8%)</span>
        </div>
      </div>
      <div class="pb">
        <div class="plbl">Posição</div>
        <div class="mr"><span style="color:var(--t3)">Caixa livre</span><span class="mono" style="font-weight:500;color:var(--ok)">R$ 4.820</span></div>
        <div class="mr"><span style="color:var(--t3)">Caixa total</span><span class="mono" style="font-weight:500;color:var(--t2)">R$ 8.180</span></div>
        <div class="mr"><span style="color:var(--t3)">Comprometido</span><span class="mono" style="font-weight:500;color:var(--warn)">R$ 3.360</span></div>
        <div class="mr"><span style="color:var(--t3)">Investido</span><span class="mono" style="font-weight:500;color:var(--t2)">R$ 187.400</span></div>
      </div>
      <div class="pb">
        <div class="plbl">Junho</div>
        <div class="mr"><span style="color:var(--t3)">Entradas</span><span class="mono" style="font-weight:500;color:var(--ok)">R$ 12.300</span></div>
        <div class="mr"><span style="color:var(--t3)">Gastos</span><span class="mono" style="font-weight:500;color:var(--t2)">R$ 8.740</span></div>
        <div class="mr">
          <span style="color:var(--t3)">Poupança</span>
          <div style="display:flex;align-items:center;gap:6px">
            <span class="mono" style="font-weight:500;color:var(--ok)">28,9%</span>
            <span style="font-size:10px;color:var(--ok)">▲ 3,1 pp</span>
          </div>
        </div>
      </div>
      <div class="pb">
        <div class="plbl">Próximas contas</div>
        <div class="mr">
          <div><div style="font-size:12px;color:var(--t1)">Conta de Luz</div><div style="font-size:10px;color:var(--alert)">25 Jun · em 3 dias</div></div>
          <span class="mono" style="font-size:12px;font-weight:500;color:var(--alert)">R$ 420</span>
        </div>
        <div class="mr">
          <div><div style="font-size:12px;color:var(--t1)">Internet Vivo</div><div style="font-size:10px;color:var(--t4)">25 Jun · débito auto</div></div>
          <span class="mono" style="font-size:12px;color:var(--t3)">R$ 139,90</span>
        </div>
        <div class="mr">
          <div><div style="font-size:12px;color:var(--t1)">Nubank Crédito</div><div style="font-size:10px;color:var(--t4)">02 Jul</div></div>
          <span class="mono" style="font-size:12px;color:var(--warn)">R$ 2.840</span>
        </div>
      </div>
    </template>

    <!-- ═══ TRANSAÇÕES PANEL ═══ -->
    <template v-else-if="isTransacoes">
      <div class="pb">
        <div class="plbl">Resumo · Junho</div>
        <div class="mr"><span style="color:var(--t3)">Entradas</span><span class="mono" style="font-weight:500;color:var(--ok)">R$ 15.800</span></div>
        <div class="mr"><span style="color:var(--t3)">Saídas</span><span class="mono" style="font-weight:500;color:var(--t2)">R$ 8.740</span></div>
        <div class="mr"><span style="color:var(--t1);font-weight:500">Saldo</span><span class="mono" style="font-size:13px;font-weight:600;color:var(--ok)">+R$ 7.060</span></div>
      </div>
      <div class="pb">
        <div class="plbl">Por categoria</div>
        <div style="margin-bottom:10px">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="font-size:11px;color:var(--t2);display:flex;align-items:center;gap:5px"><UiAppIcon name="home" :size="11" />Moradia</span><span class="mono" style="font-size:11px;color:var(--warn)">R$ 2.800</span></div>
          <div style="height:5px;background:var(--ly);border-radius:3px;overflow:hidden"><div style="width:100%;height:100%;background:var(--warn);border-radius:3px"></div></div>
        </div>
        <div style="margin-bottom:10px">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="font-size:11px;color:var(--t2);display:flex;align-items:center;gap:5px"><UiAppIcon name="restaurant" :size="11" />Restaurantes</span><span class="mono" style="font-size:11px;color:var(--warn)">R$ 1.044</span></div>
          <div style="height:5px;background:var(--ly);border-radius:3px;overflow:hidden"><div style="width:37%;height:100%;background:var(--warn);border-radius:3px"></div></div>
        </div>
        <div style="margin-bottom:10px">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="font-size:11px;color:var(--t2);display:flex;align-items:center;gap:5px"><UiAppIcon name="shopping" :size="11" />Alimentação</span><span class="mono" style="font-size:11px;color:var(--t3)">R$ 847</span></div>
          <div style="height:5px;background:var(--ly);border-radius:3px;overflow:hidden"><div style="width:30%;height:100%;background:var(--blue);border-radius:3px"></div></div>
        </div>
        <div style="margin-bottom:10px">
          <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="font-size:11px;color:var(--t2);display:flex;align-items:center;gap:5px"><UiAppIcon name="gaming" :size="11" />Lazer</span><span class="mono" style="font-size:11px;color:var(--alert)">R$ 678</span></div>
          <div style="height:5px;background:var(--ly);border-radius:3px;overflow:hidden"><div style="width:24%;height:100%;background:var(--alert);border-radius:3px"></div></div>
        </div>
        <div>
          <div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="font-size:11px;color:var(--t2);display:flex;align-items:center;gap:5px"><UiAppIcon name="car" :size="11" />Transporte</span><span class="mono" style="font-size:11px;color:var(--t3)">R$ 380</span></div>
          <div style="height:5px;background:var(--ly);border-radius:3px;overflow:hidden"><div style="width:13%;height:100%;background:var(--blue);border-radius:3px"></div></div>
        </div>
      </div>
    </template>

    <!-- ═══ ORÇAMENTO PANEL ═══ -->
    <template v-else-if="isOrcamento">
      <div class="pb">
        <div class="plbl">Saúde do orçamento</div>
        <div style="display:flex;align-items:baseline;gap:5px;margin-bottom:6px">
          <span class="mono" style="font-size:40px;font-weight:300;letter-spacing:-.03em;color:var(--warn);line-height:1">76</span>
          <span style="font-size:20px;color:var(--warn);opacity:.7">%</span>
          <span style="font-size:11px;color:var(--t3);margin-left:4px">usado</span>
        </div>
        <div style="height:6px;background:var(--ly);border-radius:3px;overflow:hidden;margin-bottom:6px"><div style="width:76%;height:100%;background:var(--warn);border-radius:3px"></div></div>
        <div style="font-size:11px;color:var(--t4)">8 dias restantes · Jun 2026</div>
      </div>
      <div class="pb">
        <div class="plbl">Resumo</div>
        <div class="mr"><span style="color:var(--t3)">Total alocado</span><span class="mono" style="color:var(--t2)">R$ 7.100</span></div>
        <div class="mr"><span style="color:var(--t3)">Total gasto</span><span class="mono" style="color:var(--warn)">R$ 5.959</span></div>
        <div class="mr"><span style="color:var(--t3)">Total livre</span><span class="mono" style="color:var(--ok)">R$ 1.141</span></div>
      </div>
      <div class="pb">
        <div class="plbl">Previsão</div>
        <div style="background:var(--wnd);border:1px solid rgba(229,144,16,0.25);border-radius:8px;padding:12px;margin-bottom:12px">
          <div style="font-size:12px;color:var(--warn);font-weight:500;margin-bottom:3px">Projeção: R$ 7.250</div>
          <div style="font-size:11px;color:var(--t3)">+R$ 150 acima do orçamento se o ritmo continuar</div>
        </div>
        <div style="background:var(--ald);border:1px solid rgba(232,53,53,0.25);border-radius:8px;padding:12px;display:flex;align-items:center;gap:10px">
          <div style="color:var(--alert);flex-shrink:0"><UiAppIcon name="gaming" :size="18" /></div>
          <div>
            <div style="font-size:12px;font-weight:600;color:var(--alert)">Lazer estourado</div>
            <div style="font-size:11px;color:var(--t3)">R$ 78 acima do limite</div>
          </div>
        </div>
      </div>
    </template>

    <!-- ═══ INVESTIMENTOS PANEL ═══ -->
    <template v-else-if="isInvestimentos">
      <div class="pb">
        <div class="plbl">Retorno acumulado</div>
        <div style="display:flex;align-items:baseline;gap:5px;margin-bottom:3px">
          <span style="font-size:13px;color:var(--ok)">▲</span>
          <span class="mono" style="font-size:38px;font-weight:200;letter-spacing:-.04em;line-height:1;background:linear-gradient(175deg,#5CEDB0 0%,#0DB878 70%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 16px rgba(13,184,120,0.28))">14,2%</span>
        </div>
        <div class="mono" style="font-size:13px;color:var(--ok);margin-bottom:2px">+ R$ 23.380 de lucro</div>
        <div style="font-size:11px;color:var(--t4)">Custo total: R$ 164.020</div>
      </div>
      <div class="pb">
        <div class="plbl">Comparativo · Junho</div>
        <div class="mr">
          <div style="display:flex;align-items:center;gap:6px"><div style="width:6px;height:6px;border-radius:2px;background:var(--blue)"></div><span style="color:var(--t2)">Carteira</span></div>
          <span class="mono" style="font-weight:500;color:var(--ok)">+2,8%</span>
        </div>
        <div class="mr">
          <div style="display:flex;align-items:center;gap:6px"><div style="width:6px;height:6px;border-radius:2px;background:var(--warn)"></div><span style="color:var(--t2)">IBOVESPA</span></div>
          <span class="mono" style="color:var(--t2)">+1,9%</span>
        </div>
        <div class="mr">
          <div style="display:flex;align-items:center;gap:6px"><div style="width:6px;height:6px;border-radius:2px;background:var(--t4)"></div><span style="color:var(--t2)">CDI</span></div>
          <span class="mono" style="color:var(--t3)">+0,8%</span>
        </div>
        <div style="margin-top:10px;font-size:11px;color:var(--ok)">▲ Acima do CDI em 2,0 p.p. no mês</div>
      </div>
      <div class="pb">
        <div class="plbl">Posição</div>
        <div class="mr"><span style="color:var(--t3)">Custo total</span><span class="mono" style="color:var(--t2)">R$ 164.020</span></div>
        <div class="mr"><span style="color:var(--t3)">Valor atual</span><span class="mono" style="color:var(--t2)">R$ 187.400</span></div>
        <div class="mr"><span style="color:var(--t1);font-weight:500">Lucro</span><span class="mono" style="font-size:13px;font-weight:600;color:var(--ok)">+R$ 23.380</span></div>
      </div>
    </template>

    <!-- ═══ CONTAS PANEL ═══ -->
    <template v-else-if="isContas">
      <div class="pb">
        <div class="plbl">Caixa disponível</div>
        <div class="mono" style="font-size:30px;font-weight:200;letter-spacing:-.04em;color:var(--t1);line-height:1;margin-bottom:5px">R$ 8.940</div>
        <div style="font-size:12px;color:var(--t4)">Nubank + BTG + Itaú</div>
      </div>
      <div class="pb">
        <div class="plbl">Por instituição</div>
        <div class="mr"><div style="display:flex;align-items:center;gap:6px"><div style="width:6px;height:6px;border-radius:2px;background:var(--bank-nubank)"></div><span style="color:var(--t2)">Nubank</span></div><span class="mono" style="color:var(--t2)">R$ 3.420</span></div>
        <div class="mr"><div style="display:flex;align-items:center;gap:6px"><div style="width:6px;height:6px;border-radius:2px;background:var(--blue)"></div><span style="color:var(--t2)">BTG Pactual</span></div><span class="mono" style="color:var(--t2)">R$ 4.760</span></div>
        <div class="mr"><div style="display:flex;align-items:center;gap:6px"><div style="width:6px;height:6px;border-radius:2px;background:var(--bank-itau)"></div><span style="color:var(--t2)">Itaú</span></div><span class="mono" style="color:var(--t2)">R$ 760</span></div>
      </div>
      <div class="pb">
        <div class="plbl">Faturas abertas</div>
        <div class="mr">
          <div><div style="font-size:12px;color:var(--t1)">Nubank Crédito</div><div style="font-size:10px;color:var(--t4)">vence 02 Jul · 10 dias</div></div>
          <span class="mono" style="font-size:12px;color:var(--warn)">R$ 2.840</span>
        </div>
        <div class="mr">
          <div><div style="font-size:12px;color:var(--t1)">Itaú Platinum</div><div style="font-size:10px;color:var(--t4)">vence 08 Jul · 16 dias</div></div>
          <span class="mono" style="font-size:12px;color:var(--t2)">R$ 1.320</span>
        </div>
      </div>
      <div class="pb">
        <div style="background:var(--ald);border:1px solid rgba(232,53,53,0.2);border-radius:8px;padding:12px;display:flex;align-items:flex-start;gap:8px">
          <div style="width:6px;height:6px;border-radius:50%;background:var(--alert);animation:pulse 2s infinite;flex-shrink:0;margin-top:4px"></div>
          <div>
            <div style="font-size:12px;font-weight:500;color:var(--alert);margin-bottom:2px">Itaú desatualizado</div>
            <div style="font-size:11px;color:var(--t3)">Saldo pode estar incorreto. Sincronize antes de tomar decisões.</div>
          </div>
        </div>
      </div>
    </template>

  </aside>
</template>

<script setup lang="ts">
const route = useRoute()
const isDashboard    = computed(() => route.path === '/' || route.path === '/dashboard')
const isTransacoes   = computed(() => route.path.startsWith('/transacoes'))
const isOrcamento    = computed(() => route.path.startsWith('/orcamento'))
const isInvestimentos = computed(() => route.path.startsWith('/investimentos'))
const isContas       = computed(() => route.path.startsWith('/contas'))
</script>
