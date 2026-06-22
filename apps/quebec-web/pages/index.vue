<template>
  <div>
    <AppNav />

    <main>
      <HeroSection />

      <div class="section-divider" />

      <PrinciplesSection />

      <div class="section-divider" />

      <ProductsSection />

      <div class="section-divider" />

      <ProcessSection />

      <div class="section-divider" />

      <PhilosophySection />

      <div class="section-divider" />

      <ContactSection />
    </main>

    <AppFooter />
  </div>
</template>

<script setup lang="ts">
useSeoMeta({
  title: 'Quebec — Software independente',
  description:
    'Ferramentas de precisão para a vida real. Construímos software que transforma sistemas complexos em experiências simples, rápidas e duráveis.',
  ogTitle: 'Quebec — Software independente',
  ogDescription:
    'Ferramentas de precisão para a vida real.',
  ogUrl: 'https://quebec.com.br',
})
</script>
