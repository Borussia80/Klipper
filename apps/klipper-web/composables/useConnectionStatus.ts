export function useConnectionStatus() {
  const isOnline = useState<boolean>('klipper-connection-online', () =>
    import.meta.client ? navigator.onLine : true
  )

  function markOnline() {
    isOnline.value = true
  }

  function markOffline() {
    isOnline.value = false
  }

  onMounted(() => {
    window.addEventListener('online', markOnline)
    window.addEventListener('offline', markOffline)
  })

  onUnmounted(() => {
    window.removeEventListener('online', markOnline)
    window.removeEventListener('offline', markOffline)
  })

  return {
    isOnline: readonly(isOnline),
    isOffline: computed(() => !isOnline.value),
  }
}
