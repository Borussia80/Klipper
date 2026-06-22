<template>
  <div class="product-card">
    <!-- Status badge -->
    <span class="status-badge" :class="`status-${status}`">
      {{ statusLabel }}
    </span>

    <!-- Icon -->
    <div class="card-icon" aria-hidden="true">
      <img v-if="icon.startsWith('/')" :src="icon" width="48" height="48" :alt="name" class="card-icon-img" />
      <span v-else v-html="icon" />
    </div>

    <!-- Content -->
    <div class="card-content">
      <h3 class="card-name">{{ name }}</h3>
      <p class="card-category mono">{{ category }}</p>
      <p class="card-desc">{{ description }}</p>
    </div>

    <!-- CTA -->
    <a
      v-if="ctaUrl && ctaUrl !== '#'"
      :href="ctaUrl"
      class="card-cta"
      :target="ctaUrl.startsWith('http') ? '_blank' : undefined"
      :rel="ctaUrl.startsWith('http') ? 'noopener noreferrer' : undefined"
    >
      {{ ctaLabel }} →
    </a>
    <span v-else class="card-cta card-cta--disabled">{{ ctaLabel }}</span>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  name: string
  category: string
  status: 'live' | 'building' | 'available'
  description: string
  ctaLabel: string
  ctaUrl: string
  icon: string
}>()

const statusLabel = computed(() => ({
  live: 'LIVE',
  building: 'EM DESENVOLVIMENTO',
  available: 'DISPONÍVEL',
}[props.status]))
</script>

<style scoped>
.product-card {
  background: var(--card);
  border: 1px solid var(--border);
  padding: 28px 24px;
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;
  transition: border-color 0.22s, background 0.22s, transform 0.28s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.28s;
  min-height: 340px;
}

.product-card:hover {
  border-color: var(--accent-border);
  background: var(--surface);
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
}

.product-card:hover {
  border-color: rgba(79, 123, 255, 0.3);
  background: var(--surface);
}

.status-badge {
  font-family: 'Geist Mono', monospace;
  font-size: 0.58rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  padding: 4px 8px;
  border-radius: 4px;
  align-self: flex-start;
  margin-bottom: 24px;
}

.status-live {
  color: var(--status-live);
  background: var(--status-live-bg);
  border: 1px solid var(--status-live-border);
}

.status-building {
  color: var(--status-building);
  background: var(--status-building-bg);
  border: 1px solid var(--status-building-border);
}

.status-available {
  color: var(--status-available);
  background: var(--status-available-bg);
  border: 1px solid var(--status-available-border);
}

.card-icon {
  color: var(--ink-2);
  margin-bottom: 20px;
  display: flex;
}

.card-icon-img {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  object-fit: cover;
}

.card-content {
  flex: 1;
}

.card-name {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 4px;
  letter-spacing: -0.01em;
}

.card-category {
  font-size: 0.68rem;
  letter-spacing: 0.1em;
  color: var(--ink-3);
  text-transform: uppercase;
  margin-bottom: 14px;
}

.card-desc {
  font-size: 0.85rem;
  line-height: 1.6;
  color: var(--ink-2);
  margin-bottom: 24px;
}

.card-cta {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--accent);
  text-decoration: none;
  transition: color 0.18s;
  margin-top: auto;
}

.card-cta:hover {
  color: #7BA3FF;
}

.card-cta--disabled {
  color: var(--ink-3);
  cursor: default;
}
</style>
