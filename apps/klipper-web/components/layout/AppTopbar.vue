<template>
  <header role="banner" style="display:flex;align-items:center;background:var(--bg-frame);border-bottom:1px solid var(--bd);z-index:100;position:relative">
    <!-- Brand -->
    <div class="tb-brand" style="display:flex;align-items:center;gap:10px;padding:0 16px;height:100%;border-right:1px solid var(--bd)">
      <img src="/klipper-mark.png" style="width:24px;height:24px;border-radius:5px;display:block;flex-shrink:0" alt="Klipper">
      <div class="tb-brand-label" style="font-size:14px;font-weight:700;color:var(--t1);letter-spacing:-.03em">Klipper</div>
    </div>

    <!-- Search -->
    <div style="flex:1;padding:0 16px">
      <button
        role="search"
        aria-label="Buscar transações (⌘K)"
        aria-keyshortcuts="Meta+k"
        class="tb-search-btn"
        style="display:flex;align-items:center;gap:8px;background:var(--sf);border:1px solid var(--bd2);border-radius:7px;padding:6px 12px;cursor:text;width:100%;font-family:inherit;text-align:left"
      >
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <circle cx="7" cy="7" r="4.5" stroke="var(--t4)" stroke-width="1.5"/>
          <path d="M10.5 10.5L13.5 13.5" stroke="var(--t4)" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <span class="tb-search-label" style="font-size:12px;color:var(--t4);flex:1">Buscar lançamentos, categorias, contas…</span>
        <span class="tb-search-kbd" aria-hidden="true" style="font-size:10px;color:var(--t4);background:var(--ly);border:1px solid var(--bd2);border-radius:3px;padding:1px 5px;font-family:'Space Grotesk',monospace">⌘K</span>
      </button>
    </div>

    <!-- Right actions -->
    <div style="flex-shrink:0;display:flex;align-items:center;gap:8px;padding:0 16px;height:100%">
      <button class="btn btn-p" aria-label="Criar novo lançamento" @click="useModal().open('novo-lancamento')">
        <svg width="11" height="11" viewBox="0 0 11 11" fill="none" aria-hidden="true">
          <line x1="5.5" y1="1" x2="5.5" y2="10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
          <line x1="1" y1="5.5" x2="10" y2="5.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
        </svg>
        <span class="tb-cta-label">Lançamento</span>
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

.tb-brand { width: var(--nav); flex-shrink: 0; }
.tb-search-btn { max-width: 380px; }

@media (max-width: 768px) {
  .tb-brand { width: auto; padding: 0 12px; border-right: none; }
  .tb-brand-label { display: none; }
  .tb-search-btn { max-width: none; }
  .tb-search-label,
  .tb-search-kbd { display: none; }
  .tb-cta-label { display: none; }
}
</style>
