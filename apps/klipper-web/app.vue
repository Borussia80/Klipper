<template>
  <!-- Fora do NuxtLayout: o login não usa o layout do app, e é justamente lá
       que o primeiro acesso encontra a API dormindo. -->
  <LayoutServerWakingNotice />
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
