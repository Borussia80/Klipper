export interface ImportResult {
  imported: number
  errors: string[]
}

export function useImport() {
  const { apiFetch } = useApi()
  const result = ref<ImportResult | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function uploadFile(file: File, accountId?: number) {
    isLoading.value = true
    error.value = null
    result.value = null
    try {
      const body = new FormData()
      body.append('file', file)
      if (accountId) body.append('account_id', String(accountId))
      result.value = await apiFetch<ImportResult>('/api/v1/imports', {
        method: 'POST',
        body,
      })
    } catch {
      error.value = 'Erro ao processar arquivo. Verifique o formato e tente novamente.'
    } finally {
      isLoading.value = false
    }
  }

  function reset() {
    result.value = null
    error.value = null
  }

  return { result, isLoading, error, uploadFile, reset }
}
