<template>
  <section class="hero">
    <div class="container hero-inner">
      <p class="hero-tag mono anim-tag">• Software independente</p>

      <h1 class="hero-title anim-title">
        Ferramentas de <span class="accent">precisão</span><br>
        para a vida real.
      </h1>

      <p class="hero-sub anim-sub">
        Construímos software que transforma sistemas complexos<br class="br-desktop">
        em experiências simples, rápidas e duráveis.
      </p>

      <div class="hero-ctas anim-ctas">
        <a href="#produtos" class="btn-accent">Explorar produtos →</a>
        <a href="#filosofia" class="btn-ghost">Conhecer a filosofia</a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding-top: 64px;
}

.hero-inner {
  padding-top: 80px;
  padding-bottom: 96px;
}

.hero-tag {
  font-size: 0.7rem;
  letter-spacing: 0.18em;
  color: var(--accent);
  text-transform: uppercase;
  margin-bottom: 36px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.hero-title {
  font-size: clamp(2.8rem, 5.5vw, 5.2rem);
  font-weight: 700;
  line-height: 1.06;
  color: var(--ink);
  margin-bottom: 28px;
  max-width: 820px;
}

.hero-sub {
  font-size: clamp(1rem, 1.6vw, 1.15rem);
  line-height: 1.65;
  color: var(--ink-2);
  max-width: 560px;
  margin-bottom: 44px;
}

.hero-ctas {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Hero entrance animations */
@keyframes heroFadeUp {
  from { opacity: 0; transform: translateY(48px); }
  to   { opacity: 1; transform: translateY(0); }
}

.anim-tag   { animation: heroFadeUp 1.0s  cubic-bezier(0.16, 1, 0.3, 1) 0.20s both; }
.anim-title { animation: heroFadeUp 1.1s  cubic-bezier(0.16, 1, 0.3, 1) 0.50s both; }
.anim-sub   { animation: heroFadeUp 1.0s  cubic-bezier(0.16, 1, 0.3, 1) 0.80s both; }
.anim-ctas  { animation: heroFadeUp 1.0s  cubic-bezier(0.16, 1, 0.3, 1) 1.05s both; }

.br-desktop { display: none; }

@media (min-width: 900px) {
  .br-desktop { display: block; }
}

@media (max-width: 768px) {
  .hero-inner {
    padding-top: 64px;
    padding-bottom: 72px;
  }

  .hero-ctas {
    flex-direction: column;
    align-items: flex-start;
  }

  .btn-accent,
  .btn-ghost {
    width: 100%;
    justify-content: center;
  }
}

@media (prefers-reduced-motion: reduce) {
  .anim-tag, .anim-title, .anim-sub, .anim-ctas {
    animation: none;
  }
}
</style>
