<template>
  <section id="produtos" class="products">
    <div class="container" ref="target" :class="{ 'in-view': visible }">
      <p class="section-label fade-heading">Produtos</p>
      <div class="products-header">
        <h2 class="products-title fade-heading">Produtos independentes.</h2>
        <p class="products-sub fade-heading">Cada produto resolve um problema diferente.</p>
      </div>

      <div class="products-grid">
        <ProductCard
          v-for="(p, i) in products"
          :key="p.name"
          class="fade-up"
          :style="{ transitionDelay: `${0.05 + i * 0.15}s` }"
          v-bind="p"
        />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const { target, visible } = useInView()

const codexIcon = `<svg width="36" height="36" viewBox="0 0 36 36" fill="none">
  <rect width="36" height="36" rx="8" fill="rgba(148,163,184,0.08)"/>
  <rect x="9" y="8" width="18" height="20" rx="2" stroke="#94A3B8" stroke-width="1.5"/>
  <line x1="13" y1="14" x2="23" y2="14" stroke="#94A3B8" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="13" y1="18" x2="23" y2="18" stroke="#94A3B8" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="13" y1="22" x2="19" y2="22" stroke="#94A3B8" stroke-width="1.5" stroke-linecap="round"/>
</svg>`

const writeIcon = `<svg width="36" height="36" viewBox="0 0 36 36" fill="none">
  <rect width="36" height="36" rx="8" fill="rgba(148,163,184,0.08)"/>
  <path d="M22 10l4 4L15 25H11v-4L22 10z" stroke="#94A3B8" stroke-width="1.5" stroke-linejoin="round"/>
</svg>`

const retroIcon = `<svg width="36" height="36" viewBox="0 0 36 36" fill="none">
  <rect width="36" height="36" rx="8" fill="rgba(148,163,184,0.08)"/>
  <rect x="8" y="13" width="20" height="12" rx="2" stroke="#94A3B8" stroke-width="1.5"/>
  <circle cx="24" cy="19" r="2" stroke="#94A3B8" stroke-width="1.5"/>
  <line x1="12" y1="19" x2="14" y2="19" stroke="#94A3B8" stroke-width="1.5" stroke-linecap="round"/>
  <line x1="13" y1="18" x2="13" y2="20" stroke="#94A3B8" stroke-width="1.5" stroke-linecap="round"/>
</svg>`

const products = [
  {
    name: 'Klipper',
    category: 'Wealth Operating System',
    status: 'live' as const,
    description: 'Sistema operacional financeiro pessoal. Patrimônio, fluxo de caixa e orçamento em tempo real.',
    ctaLabel: 'Abrir Klipper',
    ctaUrl: 'https://klipper.quebec.com.br',
    icon: '/images/klipper-icon-dark.png',
  },
  {
    name: 'Codex',
    category: 'Knowledge System',
    status: 'building' as const,
    description: 'Base de conhecimento pessoal e documentação. Organize, conecte e encontre.',
    ctaLabel: 'Saiba mais',
    ctaUrl: '#',
    icon: codexIcon,
  },
  {
    name: 'DailyWrite',
    category: 'Writing Tool',
    status: 'building' as const,
    description: 'Ambiente minimalista de escrita. Uma página por dia. Foco no que importa.',
    ctaLabel: 'Saiba mais',
    ctaUrl: '#',
    icon: writeIcon,
  },
  {
    name: 'RetroManager',
    category: 'Retro Gaming',
    status: 'available' as const,
    description: 'Gerenciador de ROMs para Linux. Organize, lance e mantenha sua biblioteca retro.',
    ctaLabel: 'Ver no GitHub',
    ctaUrl: 'https://github.com/Borussia80',
    icon: retroIcon,
  },
]
</script>

<style scoped>
.products {
  padding: 96px 0;
}

.products-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 40px;
  gap: 24px;
  flex-wrap: wrap;
}

.products-title {
  font-size: clamp(1.8rem, 3vw, 2.4rem);
  font-weight: 700;
  color: var(--ink);
}

.products-sub {
  font-size: 0.9rem;
  color: var(--ink-2);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

@media (max-width: 1024px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .products {
    padding: 72px 0;
  }

  .products-grid {
    grid-template-columns: 1fr;
  }
}
</style>
