<template>
  <nav class="mobile-nav" aria-label="Navegação mobile">
    <NuxtLink
      v-for="item in navItems"
      :key="item.to"
      :to="item.to"
      class="mobile-nav-item"
      :aria-label="item.label"
    >
      <span class="mnav-icon" v-html="item.icon" aria-hidden="true" />
      <span class="mnav-label">{{ item.label }}</span>
    </NuxtLink>
  </nav>
</template>

<script setup lang="ts">
const navItems = [
  {
    to: '/dashboard',
    label: 'Dashboard',
    icon: `<svg width="20" height="20" viewBox="0 0 18 18" fill="none"><rect x="2" y="2" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/><rect x="10" y="2" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/><rect x="2" y="10" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/><rect x="10" y="10" width="6" height="6" rx="1.5" stroke="currentColor" stroke-width="1.4"/></svg>`,
  },
  {
    to: '/transacoes',
    label: 'Transações',
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
  {
    to: '/contas',
    label: 'Contas',
    icon: `<svg width="20" height="20" viewBox="0 0 18 18" fill="none"><rect x="2" y="4" width="14" height="10" rx="2" stroke="currentColor" stroke-width="1.4"/><path d="M2 8h14" stroke="currentColor" stroke-width="1.4"/><circle cx="5.5" cy="11" r="1" fill="currentColor"/></svg>`,
  },
]
</script>

<style scoped>
.mobile-nav {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: rgba(21, 29, 42, 0.96);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-top: 1px solid var(--border);
  z-index: 200;
  align-items: stretch;
  padding: 0 var(--space-2);
}

.mobile-nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  color: var(--ink-3);
  text-decoration: none;
  transition: color 0.16s;
  padding: 6px 0;
  position: relative;
}

.mobile-nav-item.router-link-active {
  color: var(--accent);
}

.mobile-nav-item.router-link-active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 20%;
  right: 20%;
  height: 2px;
  background: var(--accent);
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
  .mobile-nav { display: flex; }
}
</style>
