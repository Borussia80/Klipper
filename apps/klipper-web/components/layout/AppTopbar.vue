<template>
  <header role="banner" style="display:flex;align-items:center;background:var(--bg-frame);border-bottom:1px solid var(--bd);z-index:100;position:relative">
    <!-- accent stripe (decorative) -->
    <div aria-hidden="true" style="position:absolute;bottom:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent 0%,var(--blue) 40%,var(--blt) 60%,transparent 100%);opacity:0.35;pointer-events:none"></div>
    <!-- Brand -->
    <div style="width:var(--nav);flex-shrink:0;display:flex;align-items:center;gap:10px;padding:0 16px;height:100%;border-right:1px solid var(--bd)">
      <img src="/klipper-mark.png" style="width:24px;height:24px;border-radius:5px;display:block;flex-shrink:0" alt="Klipper">
      <div style="font-size:14px;font-weight:700;color:var(--t1);letter-spacing:-.03em">Klipper</div>
    </div>

    <!-- Search -->
    <div style="flex:1;padding:0 16px">
      <button
        role="search"
        aria-label="Buscar transações (⌘K)"
        aria-keyshortcuts="Meta+k"
        style="display:flex;align-items:center;gap:8px;background:var(--sf);border:1px solid var(--bd2);border-radius:7px;padding:6px 12px;max-width:380px;cursor:text;width:100%;font-family:inherit;text-align:left"
      >
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <circle cx="7" cy="7" r="4.5" stroke="var(--t4)" stroke-width="1.5"/>
          <path d="M10.5 10.5L13.5 13.5" stroke="var(--t4)" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <span style="font-size:12px;color:var(--t4);flex:1">Buscar lançamentos, categorias, contas…</span>
        <span aria-hidden="true" style="font-size:10px;color:var(--t4);background:var(--ly);border:1px solid var(--bd2);border-radius:3px;padding:1px 5px;font-family:'JetBrains Mono',monospace">⌘K</span>
      </button>
    </div>

    <!-- Right actions -->
    <div style="width:var(--rp);flex-shrink:0;display:flex;align-items:center;gap:8px;padding:0 16px;height:100%;border-left:1px solid var(--bd);background:var(--bg-frame)">
      <div role="status" aria-live="polite" aria-label="Sincronizado" style="display:flex;align-items:center;gap:5px;font-size:11px;color:var(--t3)">
        <div aria-hidden="true" style="width:6px;height:6px;border-radius:50%;background:var(--ok);animation:pulse 2.4s ease-in-out infinite"></div>
        sincronizado
      </div>
      <button
        class="btn-i"
        aria-label="Notificações"
        aria-haspopup="true"
        style="margin-left:auto;position:relative;cursor:pointer"
      >
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <path d="M8 2.5a4 4 0 00-4 4v2.2L2.5 11h11L12 8.7V6.5a4 4 0 00-4-4ZM6.5 13a1.5 1.5 0 003 0" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span aria-hidden="true" style="position:absolute;top:-4px;right:-4px;min-width:14px;height:14px;background:var(--alert);border-radius:7px;font-size:8px;font-weight:700;color:#fff;display:flex;align-items:center;justify-content:center;border:1.5px solid var(--bg);padding:0 2px;pointer-events:none">2</span>
        <span class="sr-only">2 notificações</span>
      </button>
      <button class="btn btn-p" aria-label="Criar novo lançamento" @click="useModal().open('novo-lancamento')">
        <svg width="11" height="11" viewBox="0 0 11 11" fill="none" aria-hidden="true">
          <line x1="5.5" y1="1" x2="5.5" y2="10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          <line x1="1" y1="5.5" x2="10" y2="5.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
        </svg>
        Lançamento
      </button>
      <button class="btn-avatar" aria-label="Menu do usuário" style="width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,var(--blue),var(--blt));display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#fff;flex-shrink:0;cursor:pointer;border:none">
        <span aria-hidden="true">RM</span>
        <span class="sr-only">Roberto Milet</span>
      </button>
    </div>
  </header>
</template>

<style scoped>
.sr-only {
  position: absolute; width: 1px; height: 1px;
  padding: 0; margin: -1px; overflow: hidden;
  clip: rect(0,0,0,0); white-space: nowrap; border: 0;
}
</style>
