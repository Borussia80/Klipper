export interface ImportResult {
  imported: number
  duplicates: number
  errors: string[]
}

export interface PreviewRow {
  occurred_on: string
  description: string
  amount: string
  installment_number: number | null
  installment_total: number | null
  page: number
  metadata: Record<string, unknown>
  suggested_member_id?: number | null
  member_id?: number | null
  token: string
}

export interface PreviewWarning {
  page: number
  reason: string
}

export interface PreviewResponse {
  adapter: string
  rows: PreviewRow[]
  warnings: PreviewWarning[]
}

export function useImport() {
  const { apiFetch } = useApi()
  const result = ref<ImportResult | null>(null)
  const preview = ref<PreviewResponse | null>(null)
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

  async function previewFile(file: File, accountId?: number) {
    isLoading.value = true
    error.value = null
    preview.value = null
    try {
      const body = new FormData()
      body.append('file', file)
      if (accountId) body.append('account_id', String(accountId))
      preview.value = await apiFetch<PreviewResponse>('/api/v1/imports/preview', {
        method: 'POST',
        body,
      })
    } catch {
      error.value = 'Erro ao processar arquivo. Verifique o formato e tente novamente.'
    } finally {
      isLoading.value = false
    }
  }

  async function confirmImport(rows: PreviewRow[], accountId?: number) {
    isLoading.value = true
    error.value = null
    try {
      result.value = await apiFetch<ImportResult>('/api/v1/imports/confirm', {
        method: 'POST',
        body: { rows, account_id: accountId },
      })
      preview.value = null
    } catch {
      error.value = 'Erro ao confirmar importação. Tente novamente.'
    } finally {
      isLoading.value = false
    }
  }

  function reset() {
    result.value = null
    preview.value = null
    error.value = null
  }

  return { result, preview, isLoading, error, uploadFile, previewFile, confirmImport, reset }
}
