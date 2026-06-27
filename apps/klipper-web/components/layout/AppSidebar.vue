<template>
  <nav
    role="navigation"
    aria-label="Navegação principal"
    style="border-right:1px solid var(--bd);overflow-y:auto;display:flex;flex-direction:column;padding:12px 0;background:var(--bg-frame)"
  >
    <ul role="list" style="list-style:none;padding:0;margin:0">
      <li>
        <NuxtLink
          to="/dashboard"
          class="ni"
          :class="{ act: route.path === '/dashboard' || route.path === '/' }"
          :aria-current="(route.path === '/dashboard' || route.path === '/') ? 'page' : undefined"
        >
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
            <circle cx="7.5" cy="7.5" r="2.5" stroke="currentColor" stroke-width="1.4"/>
            <circle cx="7.5" cy="7.5" r="5.8" stroke="currentColor" stroke-width="1.4" stroke-dasharray="2.5 2.5" stroke-dashoffset="1.25"/>
          </svg>
          Painel
          <span style="margin-left:auto;font-size:10px;background:var(--ald);color:var(--alert);border-radius:10px;padding:1px 6px;font-weight:500" aria-label="2 alertas">2</span>
        </NuxtLink>
      </li>
      <li>
        <NuxtLink
          to="/transacoes"
          class="ni"
          :class="{ act: route.path.startsWith('/transacoes') }"
          :aria-current="route.path.startsWith('/transacoes') ? 'page' : undefined"
        >
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
            <path d="M2 11l3-3 2.5 2 4.5-6" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Movimento
        </NuxtLink>
      </li>
      <li>
        <NuxtLink
          to="/orcamento"
          class="ni"
          :class="{ act: route.path.startsWith('/orcamento') }"
          :aria-current="route.path.startsWith('/orcamento') ? 'page' : undefined"
        >
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
            <rect x="2" y="3" width="11" height="9" rx="1.5" stroke="currentColor" stroke-width="1.4"/>
            <path d="M5 3V2.5M10 3V2.5M2 6h11" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
          Orçamento
          <span style="margin-left:auto;font-size:10px;background:var(--wnd);color:var(--warn);border-radius:10px;padding:1px 6px;font-weight:500" aria-label="87% do orçamento usado">87%</span>
        </NuxtLink>
      </li>

      <li><div style="height:1px;background:var(--bd);margin:6px 12px" aria-hidden="true"></div></li>

      <li>
        <NuxtLink
          to="/investimentos"
          class="ni"
          :class="{ act: route.path.startsWith('/investimentos') }"
          :aria-current="route.path.startsWith('/investimentos') ? 'page' : undefined"
        >
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
            <rect x="2" y="9" width="3" height="4" rx="1" stroke="currentColor" stroke-width="1.4"/>
            <rect x="6" y="6" width="3" height="7" rx="1" stroke="currentColor" stroke-width="1.4"/>
            <rect x="10" y="3" width="3" height="10" rx="1" stroke="currentColor" stroke-width="1.4"/>
          </svg>
          Patrimônio
        </NuxtLink>
      </li>
      <li>
        <NuxtLink
          to="/contas"
          class="ni"
          :class="{ act: route.path.startsWith('/contas') }"
          :aria-current="route.path.startsWith('/contas') ? 'page' : undefined"
        >
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
            <rect x="2" y="2" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.4"/>
            <rect x="8" y="2" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.4"/>
            <rect x="2" y="8" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.4"/>
            <rect x="8" y="8" width="5" height="5" rx="1" stroke="currentColor" stroke-width="1.4"/>
          </svg>
          Carteiras
          <span style="margin-left:auto;font-size:10px;background:var(--ly);color:var(--t4);border-radius:10px;padding:1px 6px;font-weight:500" aria-label="4 contas">4</span>
        </NuxtLink>
      </li>

      <li><div style="height:1px;background:var(--bd);margin:6px 12px" aria-hidden="true"></div></li>

      <li>
        <NuxtLink
          to="/kira"
          class="ni"
          :class="{ act: route.path.startsWith('/kira') }"
          :aria-current="route.path.startsWith('/kira') ? 'page' : undefined"
        >
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
            <circle cx="7.5" cy="7.5" r="1.5" fill="currentColor"/>
            <path d="M7.5 2.5v1.5M7.5 11v1.5M2.5 7.5H4M11 7.5h1.5M4.2 4.2l1.1 1.1M9.7 9.7l1.1 1.1M9.7 4.2l-1.1 1.1M4.2 9.7l1.1 1.1" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
          Kira
          <span style="margin-left:auto;font-size:9px;background:var(--bdm);color:var(--blue);border-radius:4px;padding:1px 5px;font-weight:600" aria-label="Beta">BETA</span>
        </NuxtLink>
      </li>
      <li>
        <NuxtLink
          to="/importar"
          class="ni"
          :class="{ act: route.path.startsWith('/importar') }"
          :aria-current="route.path.startsWith('/importar') ? 'page' : undefined"
        >
          <svg width="15" height="15" viewBox="0 0 15 15" fill="none" aria-hidden="true">
            <path d="M7.5 2v7M5 6.5l2.5 3 2.5-3M3 10v2a1 1 0 001 1h7a1 1 0 001-1v-2" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Importar
        </NuxtLink>
      </li>
    </ul>

    <div style="padding:10px 12px 0">
      <button
        class="btn btn-p"
        style="width:100%"
        aria-label="Criar novo lançamento"
        @click="open('novo-lancamento')"
      >
        <svg width="11" height="11" viewBox="0 0 11 11" fill="none" aria-hidden="true">
          <line x1="5.5" y1="1" x2="5.5" y2="10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          <line x1="1" y1="5.5" x2="10" y2="5.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
        </svg>
        Novo lançamento
      </button>
    </div>

    <div style="display:flex;flex-wrap:wrap;gap:8px;padding:12px 20px;margin-top:auto" aria-label="Atalhos de teclado">
      <span style="display:flex;align-items:center;gap:3px;font-size:10px;color:var(--t4)"><kbd>N</kbd> novo</span>
      <span style="display:flex;align-items:center;gap:3px;font-size:10px;color:var(--t4)"><kbd>K</kbd> buscar</span>
      <span style="display:flex;align-items:center;gap:3px;font-size:10px;color:var(--t4)"><kbd>?</kbd> ajuda</span>
    </div>
  </nav>
</template>

<script setup lang="ts">
const route = useRoute()
const { open } = useModal()
</script>

<style scoped>
.sr-only {
  position: absolute; width: 1px; height: 1px;
  padding: 0; margin: -1px; overflow: hidden;
  clip: rect(0,0,0,0); white-space: nowrap; border: 0;
}
</style>
