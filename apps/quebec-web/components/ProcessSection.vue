<template>
  <section id="processo" class="process">
    <div class="container" ref="target" :class="{ 'in-view': visible }">
      <p class="section-label fade-heading">Como trabalhamos</p>
      <h2 class="process-title fade-heading">Do problema<br>ao produto.</h2>

      <div class="steps">
        <div
          v-for="(step, i) in steps"
          :key="step.title"
          class="step fade-up"
          :style="{ transitionDelay: `${0.05 + i * 0.15}s` }"
        >
          <span class="step-number mono">0{{ i + 1 }}</span>
          <h3 class="step-title">{{ step.title }}</h3>
          <p class="step-text">{{ step.text }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const { target, visible } = useInView()

const steps = [
  {
    title: 'Diagnóstico',
    text: 'Entendemos o problema antes de escrever uma linha de código. Clareza sobre o objetivo define a qualidade do resultado.',
  },
  {
    title: 'Arquitetura',
    text: 'Projetamos sistemas para durar anos. Decisões técnicas tomadas com critério — sem modismos, sem complexidade desnecessária.',
  },
  {
    title: 'Construção',
    text: 'Código revisado, testado e entregue com documentação clara. Cada entrega é um produto, não um protótipo.',
  },
  {
    title: 'Evolução',
    text: 'Software não termina no lançamento. Iteramos com base em uso real, melhorando de forma incremental e contínua.',
  },
]
</script>

<style scoped>
.process {
  padding: 96px 0;
}

.process-title {
  font-size: clamp(1.8rem, 3vw, 2.4rem);
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 64px;
  line-height: 1.15;
}

.steps {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0;
  border: 1px solid var(--border);
}

.step {
  padding: 36px 32px;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: background 0.22s;
}

.step:hover {
  background: rgba(255,255,255,0.02);
}

.step:last-child {
  border-right: none;
}

.step-number {
  font-size: 0.65rem;
  letter-spacing: 0.12em;
  color: var(--accent);
}

.step-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.01em;
  line-height: 1.2;
}

.step-text {
  font-size: 0.875rem;
  color: var(--ink-2);
  line-height: 1.7;
}

@media (max-width: 900px) {
  .steps {
    grid-template-columns: repeat(2, 1fr);
  }

  .step {
    border-right: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
  }

  .step:nth-child(2n) {
    border-right: none;
  }

  .step:nth-child(3),
  .step:nth-child(4) {
    border-bottom: none;
  }
}

@media (max-width: 560px) {
  .process {
    padding: 72px 0;
  }

  .steps {
    grid-template-columns: 1fr;
  }

  .step {
    border-right: none;
    border-bottom: 1px solid var(--border);
  }

  .step:last-child {
    border-bottom: none;
  }
}
</style>
