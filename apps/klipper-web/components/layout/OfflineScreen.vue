<template>
  <section class="offline-screen" role="alert" aria-live="polite">
    <div class="offline-mark" aria-hidden="true">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
        <path d="M4 9.5a8 8 0 0 1 16 0M7.5 13a4.5 4.5 0 0 1 9 0M11 16.5h2" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
        <path d="m4 4 16 16" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
      </svg>
    </div>
    <h1>Você está sem conexão</h1>
    <p>O Klipper precisa da internet para consultar seus dados financeiros. Assim que a conexão voltar, tente novamente.</p>
  </section>
</template>

<style scoped>
.offline-screen {
  display: grid;
  place-items: center;
  align-content: center;
  gap: 12px;
  min-height: min(70vh, 520px);
  padding: 32px 20px;
  text-align: center;
  color: var(--t2);
}

.offline-mark {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  border: 1px solid var(--bd2);
  border-radius: 50%;
  color: var(--warn);
  background: var(--sf);
}

h1 { margin: 0; color: var(--t1); font-size: 19px; font-weight: 600; }
p { max-width: 380px; margin: 0; color: var(--t3); font-size: 13px; line-height: 1.55; }
</style>
