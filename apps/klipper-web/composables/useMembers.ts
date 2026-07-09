export interface Member {
  id: number
  name: string
  relationship: 'titular' | 'dependente'
  active: boolean
  created_at: string
  updated_at: string
}

export function useMembers() {
  const { apiFetch } = useApi()
  const { addToast } = useToast()
  const members = useState<Member[]>('members', () => [])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchMembers() {
    isLoading.value = true
    error.value = null
    try {
      members.value = await apiFetch<Member[]>('/api/v1/members')
    } catch {
      error.value = 'Erro ao carregar portadores.'
    } finally {
      isLoading.value = false
    }
  }

  async function createMember(payload: Partial<Member>) {
    const data = await apiFetch<Member>('/api/v1/members', {
      method: 'POST',
      body: payload,
    })
    members.value = [...members.value, data]
    addToast('Portador adicionado', 'ok')
    return data
  }

  async function updateMember(id: number, payload: Partial<Member>) {
    const data = await apiFetch<Member>(`/api/v1/members/${id}`, {
      method: 'PATCH',
      body: payload,
    })
    members.value = members.value.map((m) => (m.id === id ? data : m))
    addToast('Portador atualizado', 'ok')
    return data
  }

  async function deleteMember(id: number) {
    await apiFetch(`/api/v1/members/${id}`, { method: 'DELETE' })
    members.value = members.value.filter((m) => m.id !== id)
    addToast('Portador removido', 'ok')
  }

  return { members, isLoading, error, fetchMembers, createMember, updateMember, deleteMember }
}
