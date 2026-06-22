<template>
  <section id="principios" class="principles">
    <div class="container" ref="target" :class="{ 'in-view': visible }">
      <p class="section-label fade-heading">Como construímos</p>
      <h2 class="principles-title fade-heading">Princípios que guiam<br>cada decisão.</h2>

      <div class="principles-grid">
        <div v-for="p in principles" :key="p.name" class="principle-card fade-up">
          <div class="principle-icon" aria-hidden="true" v-html="p.icon" />
          <h3 class="principle-name">{{ p.name }}</h3>
          <p class="principle-desc">{{ p.desc }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const { target, visible } = useInView()
const principles = [
  {
    name: 'Precisão',
    desc: 'Clareza técnica em cada decisão. Um produto faz uma coisa muito bem, sem tentar abraçar todo o problema de uma vez.',
    icon: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none">
      <circle cx="14" cy="14" r="12" stroke="currentColor" stroke-width="1.5" opacity="0.3"/>
      <circle cx="14" cy="14" r="6" stroke="currentColor" stroke-width="1.5" opacity="0.6"/>
      <circle cx="14" cy="14" r="2" fill="currentColor"/>
      <line x1="14" y1="2" x2="14" y2="6" stroke="currentColor" stroke-width="1.5" opacity="0.4"/>
      <line x1="14" y1="22" x2="14" y2="26" stroke="currentColor" stroke-width="1.5" opacity="0.4"/>
      <line x1="2" y1="14" x2="6" y2="14" stroke="currentColor" stroke-width="1.5" opacity="0.4"/>
      <line x1="22" y1="14" x2="26" y2="14" stroke="currentColor" stroke-width="1.5" opacity="0.4"/>
    </svg>`,
  },
  {
    name: 'Simplicidade',
    desc: 'Menos funcionalidades, mais propósito. Interfaces limpas, fluxos diretos. Menos é mais quando cada detalhe tem razão de existir.',
    icon: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none">
      <line x1="4" y1="9"  x2="24" y2="9"  stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <line x1="4" y1="14" x2="18" y2="14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity="0.7"/>
      <line x1="4" y1="19" x2="12" y2="19" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity="0.4"/>
    </svg>`,
  },
  {
    name: 'Longevidade',
    desc: 'Construído para durar anos, não sprints. Tecnologias maduras, código sustentável, evolução contínua sem ruptura forçada.',
    icon: `<svg width="28" height="28" viewBox="0 0 28 28" fill="none">
      <path d="M4 14C4 14 7 8 11 8C15 8 13 20 17 20C21 20 24 14 24 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" fill="none"/>
    </svg>`,
  },
]
</script>

<style scoped>
.principles {
  padding: 96px 0;
}

.principles-title {
  font-size: clamp(1.8rem, 3vw, 2.4rem);
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 56px;
  max-width: 480px;
}

.principles-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2px;
}

.principle-card {
  background: var(--card);
  border: 1px solid var(--border);
  padding: 36px 32px;
  transition: background 0.22s, border-color 0.22s, transform 0.28s cubic-bezier(0.22, 1, 0.36, 1);
}

.principle-card:hover {
  background: var(--surface);
  border-color: var(--accent-border);
  transform: translateY(-3px);
}

.principle-card + .principle-card {
  border-left: none;
}

.principle-icon {
  color: var(--accent);
  margin-bottom: 20px;
  display: flex;
}

.principle-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 10px;
  letter-spacing: -0.01em;
}

.principle-desc {
  font-size: 0.875rem;
  line-height: 1.65;
  color: var(--ink-2);
}

@media (max-width: 768px) {
  .principles {
    padding: 72px 0;
  }

  .principles-grid {
    grid-template-columns: 1fr;
    gap: 0;
  }

  .principle-card + .principle-card {
    border-left: 1px solid var(--border);
    border-top: none;
  }
}
</style>
