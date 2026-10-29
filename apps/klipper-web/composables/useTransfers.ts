export interface TransferPayload {
  source_account_id: number
  destination_account_id: number
  amount: string
  occurred_on: string
  description: string
  status?: 'previsto' | 'efetivado' | 'conciliado'
}

export function useTransfers() {
  const { apiFetch } = useApi()
  const { addToast } = useToast()

  async function createTransfer(payload: TransferPayload) {
    const result = await apiFetch('/api/v1/transfers', { method: 'POST', body: payload })
    addToast('Transferência registrada', 'ok')
    return result
  }

  return { createTransfer }
}
