<template>
  <nav class="nav">
    <div class="container nav-inner">
      <!-- Brand -->
      <a href="/" class="nav-brand" aria-label="Quebec — página inicial">
        <span class="brand-wordmark nav-wordmark">Quebec</span>
        <span class="nav-pipe" aria-hidden="true">|</span>
        <span class="nav-tagline">Software independente</span>
      </a>

      <!-- Links -->
      <div class="nav-links">
        <a href="#produtos">Produtos</a>
        <a href="#processo">Processo</a>
        <a href="#filosofia">Filosofia</a>
        <a href="#contato">Contato</a>
      </div>

      <!-- CTA -->
      <a href="#produtos" class="btn-accent nav-cta">Explorar produtos →</a>

      <!-- Mobile hamburger -->
      <button
        class="nav-hamburger"
        :aria-expanded="menuOpen"
        aria-label="Menu"
        @click="menuOpen = !menuOpen"
      >
        <span />
        <span />
        <span />
      </button>
    </div>

    <!-- Mobile menu -->
    <div v-if="menuOpen" class="nav-mobile">
      <a href="#produtos" @click="menuOpen = false">Produtos</a>
      <a href="#processo" @click="menuOpen = false">Processo</a>
      <a href="#filosofia" @click="menuOpen = false">Filosofia</a>
      <a href="#contato" @click="menuOpen = false">Contato</a>
      <a href="#produtos" class="btn-accent" @click="menuOpen = false">Explorar produtos →</a>
    </div>
  </nav>
</template>

<script setup lang="ts">
const menuOpen = ref(false)
</script>

<style scoped>
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(6, 10, 18, 0.88);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
}

.nav-inner {
  display: flex;
  align-items: center;
  height: 64px;
  gap: 32px;
}

.nav-brand {
  display: flex;
  align-items: center;
  text-decoration: none;
  flex-shrink: 0;
}

.nav-wordmark {
  font-size: 1.05rem;
  color: var(--ink);
  letter-spacing: 0.14em;
}

.nav-pipe {
  color: var(--border);
  font-weight: 300;
  margin: 0 14px;
  font-size: 1.1rem;
  line-height: 1;
}

.nav-tagline {
  font-size: 0.78rem;
  color: var(--ink-2);
  letter-spacing: 0.01em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 28px;
  flex: 1;
  margin-left: 16px;
}

.nav-links a {
  font-size: 0.875rem;
  color: var(--ink-2);
  text-decoration: none;
  transition: color 0.18s;
}

.nav-links a:hover {
  color: var(--ink);
}

.nav-cta {
  flex-shrink: 0;
  font-size: 0.8rem;
  padding: 9px 18px;
}

.nav-hamburger {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  width: 22px;
  height: 16px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  margin-left: auto;
}

.nav-hamburger span {
  display: block;
  height: 1.5px;
  background: var(--ink-2);
  border-radius: 1px;
  transition: background 0.18s;
}

.nav-hamburger:hover span {
  background: var(--ink);
}

.nav-mobile {
  display: flex;
  flex-direction: column;
  gap: 0;
  border-top: 1px solid var(--border);
  padding: 8px 24px 20px;
}

.nav-mobile a {
  display: block;
  padding: 12px 0;
  font-size: 0.9rem;
  color: var(--ink-2);
  text-decoration: none;
  border-bottom: 1px solid var(--border);
  transition: color 0.18s;
}

.nav-mobile a:hover {
  color: var(--ink);
}

.nav-mobile .btn-accent {
  margin-top: 16px;
  justify-content: center;
  border-bottom: none;
}

@media (max-width: 768px) {
  .nav-links, .nav-cta {
    display: none;
  }

  .nav-hamburger {
    display: flex;
  }
}

@media (max-width: 600px) {
  .nav-tagline {
    display: none;
  }

  .nav-pipe {
    display: none;
  }
}
</style>
