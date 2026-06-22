export function useInView() {
  const target = ref<HTMLElement | null>(null)
  const visible = ref(false)

  onMounted(() => {
    if (!target.value) return
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          visible.value = true
          obs.disconnect()
        }
      },
      {
        threshold: 0.15,
        rootMargin: '0px 0px -22% 0px',
      }
    )
    obs.observe(target.value)
  })

  return { target, visible }
}
