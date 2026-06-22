<template>
  <section id="contato" class="contact">
    <div class="container contact-inner">
      <div class="contact-icon" aria-hidden="true">
        <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
          <rect width="40" height="40" rx="8" fill="var(--accent-dim)" stroke="var(--accent-border)" stroke-width="1"/>
          <rect x="8" y="13" width="24" height="16" rx="2" stroke="#4F7BFF" stroke-width="1.5"/>
          <path d="M8 16l12 9 12-9" stroke="#4F7BFF" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <h2 class="contact-title">Vamos conversar.</h2>

      <p class="contact-sub">
        Aberto a feedback, colaborações e discussões técnicas.
      </p>

      <div class="contact-ctas">
        <a
          href="https://github.com/quebec-studio"
          target="_blank"
          rel="noopener noreferrer"
          class="btn-ghost"
        >
          GitHub ↗
        </a>
        <a
          href="mailto:contato@quebec.com.br"
          class="btn-accent"
        >
          Enviar e-mail
        </a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.contact {
  padding: 96px 0;
}

.contact-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.contact-icon {
  margin-bottom: 24px;
}

.contact-title {
  font-size: clamp(2rem, 3.5vw, 2.8rem);
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 16px;
}

.contact-sub {
  font-size: 1rem;
  color: var(--ink-2);
  margin-bottom: 36px;
  max-width: 360px;
  line-height: 1.6;
}

.contact-ctas {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

@media (max-width: 480px) {
  .contact {
    padding: 72px 0;
  }

  .contact-ctas {
    flex-direction: column;
    width: 100%;
  }

  .btn-accent,
  .btn-ghost {
    justify-content: center;
    width: 100%;
  }
}
</style>
