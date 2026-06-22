<template>
  <section id="filosofia" class="philosophy">
    <div class="container philosophy-grid">
      <div class="philosophy-left">
        <p class="section-label">Nossa filosofia</p>
        <h2 class="philosophy-title">Software pequeno.<br>Problemas reais.</h2>
      </div>

      <div class="philosophy-right">
        <p class="philosophy-text">
          Criamos ferramentas digitais que priorizam utilidade diária, simplicidade e longevidade.
        </p>
        <p class="philosophy-text">
          Cada produto nasce para resolver um problema específico.<br>
          Sem excesso de funcionalidades.<br>
          Sem complexidade desnecessária.<br>
          Sem ruído.
        </p>
        <p class="philosophy-text">
          Software que você instala e não quer mais desinstalar.
        </p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.philosophy {
  padding: 96px 0;
}

.philosophy-grid {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 80px;
  align-items: start;
}

.philosophy-title {
  font-size: clamp(1.6rem, 2.5vw, 2rem);
  font-weight: 700;
  color: var(--ink);
  line-height: 1.2;
}

.philosophy-right {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-top: 4px;
}

.philosophy-text {
  font-size: 0.95rem;
  line-height: 1.75;
  color: var(--ink-2);
}

@media (max-width: 900px) {
  .philosophy {
    padding: 72px 0;
  }

  .philosophy-grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }
}
</style>
