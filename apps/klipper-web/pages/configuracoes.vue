<template>
  <div class="configuracoes">
    <div class="page-header">
      <div>
        <h2 class="page-h2">Configurações</h2>
        <p class="page-sub mono">Klipper v0.1.0</p>
      </div>
    </div>

    <div class="settings-grid">
      <div class="card settings-card">
        <p class="section-label">Conta</p>
        <div class="setting-row">
          <div>
            <p class="setting-name">Roberto Milet</p>
            <p class="setting-sub">roberto.milet@gmail.com</p>
          </div>
          <button class="btn btn-ghost btn-sm">Editar</button>
        </div>
      </div>

      <div class="card settings-card">
        <p class="section-label">Aparência</p>
        <div class="setting-row">
          <p class="setting-name">Tema</p>
          <span class="badge badge--neutral">Escuro</span>
        </div>
        <div class="setting-row">
          <p class="setting-name">Moeda</p>
          <span class="badge badge--neutral mono">BRL</span>
        </div>
      </div>

      <div class="card settings-card">
        <p class="section-label">Sincronização</p>
        <div class="setting-row">
          <div>
            <p class="setting-name">API Klipper</p>
            <p class="setting-sub mono">railway.app · conectado</p>
          </div>
          <span class="badge badge--positive">Online</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', title: 'Configurações' })
</script>

<style scoped>
.configuracoes {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  padding-bottom: 80px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}

.page-h2 {
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 4px;
}

.page-sub { font-size: 0.78rem; color: var(--ink-3); }

.settings-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  max-width: 640px;
}

.settings-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--rule);
}

.setting-row:last-child { border-bottom: none; }

.setting-name {
  font-size: 0.875rem;
  color: var(--ink);
}

.setting-sub {
  font-size: 0.72rem;
  color: var(--ink-3);
  margin-top: 2px;
}
</style>
