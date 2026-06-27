<template>
  <div
    style="background:var(--sf);border:1px solid var(--bd);border-radius:10px;padding:16px;display:flex;flex-direction:column;gap:10px"
    role="presentation"
    aria-label="Carregando..."
  >
    <div style="display:flex;align-items:center;gap:12px">
      <!-- Icon placeholder -->
      <UiSkeletonLine
        width="36px"
        height="36px"
        style="border-radius:9px;flex-shrink:0"
      />
      <!-- Text lines -->
      <div style="flex:1;display:flex;flex-direction:column;gap:6px">
        <UiSkeletonLine width="60%" height="13px" />
        <UiSkeletonLine width="40%" height="11px" />
      </div>
      <!-- Amount -->
      <UiSkeletonLine width="80px" height="15px" />
    </div>
  </div>
</template>
