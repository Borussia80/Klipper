<template>
  <div class="mobile-nav-shell">
    <div v-if="moreOpen" class="more-backdrop" aria-hidden="true" @click="moreOpen = false" />
    <section v-if="moreOpen" class="more-sheet" aria-label="Mais páginas">
      <div class="more-sheet-header">
        <span>Mais</span>
        <button type="button" class="more-close" aria-label="Fechar mais páginas" @click="moreOpen = false">×</button>
      </div>
      <NuxtLink
        v-for="item in moreItems"
        :key="item.to"
        :to="item.to"
        class="more-item"
        @click="moreOpen = false"
      >
        <span class="mnav-icon" v-html="item.icon" aria-hidden="true" />
        <span>{{ item.label }}</span>
      </NuxtLink>
    </section>

    <nav class="mobile-nav" aria-label="Navegação mobile">
    <NuxtLink
      v-for="item in fixedItems"
      :key="item.to"
      :to="item.to"
      class="mobile-nav-item"
      :aria-label="item.label"
    >
      <span class="mnav-icon" v-html="item.icon" aria-hidden="true" />
      <span class="mnav-label">{{ item.label }}</span>
    </NuxtLink>
      <button
        type="button"
        class="mobile-nav-item more-trigger"
        :class="{ active: moreOpen }"
        aria-label="Mais páginas"
        :aria-expanded="moreOpen"
        @click="moreOpen = !moreOpen"
      >
        <span class="mnav-icon more-dots" aria-hidden="true">•••</span>
        <span class="mnav-label">Mais</span>
      </button>
    </nav>
  </div>
</template>

<script setup lang="ts">
const moreOpen = ref(false)

const fixedItems = [
  {
    to: '/dashboard',
    label: 'Painel',
    icon: `<svg width="20" height="20" viewBox="0 0 18 18" fill="none"><rect x="2" y="2" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/><rect x="10" y="2" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/><rect x="2" y="10" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/><rect x="10" y="10" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/></svg>`,
  },
  {
    to: '/transacoes',
    label: 'Movimento',
    icon: `<svg width="20" height="20" viewBox="0 0 18 18" fill="none"><path d="M3 9h12M3 5h8M3 13h5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>`,
  },
  {
    to: '/orcamento',
    label: 'Orçamento',
    icon: `<svg width="20" height="20" viewBox="0 0 18 18" fill="none"><rect x="2" y="5" width="14" height="3" rx="1" stroke="currentColor" stroke-width="1.4"/><rect x="2" y="10" width="9" height="3" rx="1" stroke="currentColor" stroke-width="1.4"/></svg>`,
  },
  {
    to: '/investimentos',
    label: 'Investimentos',
    icon: `<svg width="20" height="20" viewBox="0 0 18 18" fill="none"><path d="M2 14l4-5 4 2 5-7" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/><circle cx="15" cy="4" r="1.5" fill="currentColor"/></svg>`,
  },
]

const moreItems = [
  {
    to: '/relatorios',
    label: 'Relatórios',
    icon: `<svg width="20" height="20" viewBox="0 0 18 18" fill="none"><path d="M3 14V8m4 6V4m4 10V6m4 8V2" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>`,
  },
  {
    to: '/importar',
    label: 'Importar',
    icon: `<svg width="20" height="20" viewBox="0 0 18 18" fill="none"><path d="M9 2v9m0 0 3-3m-3 3L6 8M3 13v2h12v-2" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  },
  {
    to: '/portadores',
    label: 'Portadores',
    icon: `<svg width="20" height="20" viewBox="0 0 18 18" fill="none"><circle cx="9" cy="6" r="3" stroke="currentColor" stroke-width="1.4"/><path d="M3 15c.8-2.5 2.8-3.8 6-3.8s5.2 1.3 6 3.8" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>`,
  },
  {
    to: '/configuracoes',
    label: 'Configurações',
    icon: `<svg width="20" height="20" viewBox="0 0 18 18" fill="none"><circle cx="9" cy="9" r="2.5" stroke="currentColor" stroke-width="1.4"/><path d="M9 2v2m0 10v2M2 9h2m10 0h2M4 4l1.5 1.5m7 7L14 14m0-10-1.5 1.5m-7 7L4 14" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>`,
  },
  {
    to: '/contas',
    label: 'Carteiras',
    icon: `<svg width="20" height="20" viewBox="0 0 18 18" fill="none"><rect x="2" y="4" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.4"/><path d="M2 8h14" stroke="currentColor" stroke-width="1.4"/><circle cx="5.5" cy="11" r="1" fill="currentColor"/></svg>`,
  },
]
</script>

<style scoped>
.mobile-nav-shell {
  display: none;
}

.mobile-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  height: calc(60px + env(safe-area-inset-bottom));
  background: var(--bg-frame);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-top: 1px solid var(--bd);
  z-index: 200;
  align-items: stretch;
  padding: 0 8px;
  padding: 0 8px env(safe-area-inset-bottom);
}

.more-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(3, 9, 16, 0.48);
  z-index: 198;
}

.more-sheet {
  position: fixed;
  left: 12px;
  right: 12px;
  bottom: calc(68px + env(safe-area-inset-bottom));
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  padding: 14px;
  background: var(--sf);
  border: 1px solid var(--bd2);
  border-radius: 8px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.32);
  z-index: 199;
}

.more-sheet-header {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--t1);
  font-size: 13px;
  font-weight: 600;
  padding: 0 2px 4px;
}

.more-close {
  border: 0;
  background: transparent;
  color: var(--t3);
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
}

.more-item {
  display: flex;
  align-items: center;
  gap: 9px;
  min-height: 42px;
  padding: 8px 10px;
  border: 1px solid var(--bd);
  border-radius: 6px;
  color: var(--t2);
  text-decoration: none;
  font-size: 12px;
}

.more-item.router-link-active {
  color: var(--t1);
  border-color: var(--brass);
}

.mobile-nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  color: var(--t3);
  text-decoration: none;
  transition: color 0.16s;
  padding: 6px 0;
  position: relative;
}

.mobile-nav-item.router-link-active {
  color: var(--t1);
}

.mobile-nav-item.router-link-active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 20%;
  right: 20%;
  height: 2px;
  background: var(--brass);
  border-radius: 0 0 2px 2px;
}

.mnav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 0;
}

.mnav-label {
  font-family: 'Inter', sans-serif;
  font-size: 0.58rem;
  letter-spacing: 0.02em;
}

@media (max-width: 768px) {
  .mobile-nav-shell { display: block; }
  .mobile-nav { display: flex; }
}
</style>
