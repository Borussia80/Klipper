export function useCountUp(target: Ref<number>, duration = 420) {
  const displayed = ref(target.value)
  let raf = 0

  function animate(from: number, to: number) {
    if (!import.meta.client) {
      displayed.value = to
      return
    }

    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReduced) {
      displayed.value = to
      return
    }

    const start = performance.now()

    function tick(now: number) {
      const elapsed = now - start
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      displayed.value = from + (to - from) * eased

      if (progress < 1) {
        raf = requestAnimationFrame(tick)
      } else {
        displayed.value = to
      }
    }

    cancelAnimationFrame(raf)
    raf = requestAnimationFrame(tick)
  }

  watch(
    target,
    (newVal, oldVal) => {
      const from = oldVal ?? newVal * 0.88
      animate(from, newVal)
    },
    { immediate: true },
  )

  onUnmounted(() => {
    if (import.meta.client) cancelAnimationFrame(raf)
  })

  return { displayed }
}
