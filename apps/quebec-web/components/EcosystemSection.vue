<template>
  <section id="ecossistema" class="ecosystem">
    <div class="container">
      <p class="section-label">Ecossistema</p>
      <h2 class="ecosystem-title">Um ecossistema<br>em expansão.</h2>

      <div class="ecosystem-diagram">
        <!-- Quebec root -->
        <div class="eco-root">
          <div class="eco-root-mark" aria-hidden="true">
            <svg width="36" height="27" viewBox="0 0 28 21" fill="none">
              <circle cx="3"  cy="3.5"  r="1.6" fill="white" opacity="0.25"/>
              <circle cx="10" cy="3.5"  r="1.6" fill="white" opacity="0.25"/>
              <circle cx="17" cy="3.5"  r="1.6" fill="white" opacity="0.25"/>
              <circle cx="25" cy="3.5"  r="1.6" fill="#4F7BFF"/>
              <circle cx="3"  cy="10.5" r="1.6" fill="white" opacity="0.25"/>
              <circle cx="10" cy="10.5" r="1.6" fill="white" opacity="0.25"/>
              <circle cx="17" cy="10.5" r="1.6" fill="white" opacity="0.25"/>
              <circle cx="25" cy="10.5" r="1.6" fill="#4F7BFF"/>
              <circle cx="3"  cy="17.5" r="1.6" fill="white" opacity="0.25"/>
              <circle cx="10" cy="17.5" r="1.6" fill="white" opacity="0.25"/>
              <circle cx="17" cy="17.5" r="1.6" fill="white" opacity="0.25"/>
              <circle cx="25" cy="17.5" r="1.6" fill="#4F7BFF"/>
            </svg>
          </div>
          <span class="brand-wordmark eco-root-name">Quebec</span>
          <span class="eco-root-sub mono">Software independente</span>
        </div>

        <!-- Products tree -->
        <div class="eco-tree">
          <!-- Klipper (live, with sub-modules) -->
          <div class="eco-product eco-product--live">
            <div class="eco-product-head">
              <span class="eco-dot eco-dot--live" />
              <span class="eco-product-name">Klipper</span>
              <span class="eco-badge mono">LIVE</span>
            </div>
            <div class="eco-modules">
              <span v-for="m in ['Signal', 'Flow', 'Vault', 'Envelope']" :key="m" class="eco-module mono">{{ m }}</span>
            </div>
          </div>

          <!-- Other products -->
          <div
            v-for="p in otherProducts"
            :key="p.name"
            class="eco-product"
          >
            <div class="eco-product-head">
              <span class="eco-dot" :class="`eco-dot--${p.status}`" />
              <span class="eco-product-name">{{ p.name }}</span>
              <span class="eco-badge-muted mono">{{ p.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const otherProducts = [
  { name: 'Codex', status: 'building', label: 'EM DESENVOLVIMENTO' },
  { name: 'DailyWrite', status: 'building', label: 'EM DESENVOLVIMENTO' },
  { name: 'RetroManager', status: 'available', label: 'DISPONÍVEL' },
]
</script>

<style scoped>
.ecosystem {
  padding: 96px 0;
}

.ecosystem-title {
  font-size: clamp(1.8rem, 3vw, 2.4rem);
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 56px;
}

.ecosystem-diagram {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 0;
  border: 1px solid var(--border);
  background: var(--card);
}

/* Root box */
.eco-root {
  padding: 36px 28px;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 8px;
  justify-content: center;
}

.eco-root-mark {
  margin-bottom: 8px;
}

.eco-root-name {
  font-size: 1.1rem;
  color: var(--ink);
}

.eco-root-sub {
  font-size: 0.65rem;
  letter-spacing: 0.12em;
  color: var(--ink-3);
  text-transform: uppercase;
}

/* Tree */
.eco-tree {
  padding: 24px 0;
}

.eco-product {
  padding: 16px 28px;
  border-bottom: 1px solid var(--border);
}

.eco-product:last-child {
  border-bottom: none;
}

.eco-product-head {
  display: flex;
  align-items: center;
  gap: 10px;
}

.eco-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

.eco-dot--live      { background: var(--status-live); }
.eco-dot--building  { background: var(--status-building); }
.eco-dot--available { background: var(--status-available); }

.eco-product-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.01em;
}

.eco-badge {
  font-size: 0.58rem;
  letter-spacing: 0.1em;
  color: var(--status-live);
  background: var(--status-live-bg);
  border: 1px solid var(--status-live-border);
  padding: 2px 7px;
  border-radius: 3px;
}

.eco-badge-muted {
  font-size: 0.58rem;
  letter-spacing: 0.1em;
  color: var(--ink-3);
  text-transform: uppercase;
}

/* Klipper sub-modules */
.eco-modules {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  margin-left: 16px;
  flex-wrap: wrap;
}

.eco-module {
  font-size: 0.65rem;
  letter-spacing: 0.08em;
  color: var(--ink-3);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border);
  padding: 3px 10px;
  border-radius: 3px;
}

@media (max-width: 768px) {
  .ecosystem {
    padding: 72px 0;
  }

  .ecosystem-diagram {
    grid-template-columns: 1fr;
  }

  .eco-root {
    border-right: none;
    border-bottom: 1px solid var(--border);
    flex-direction: row;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    padding: 24px;
  }
}
</style>
