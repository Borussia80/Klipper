export interface Category {
  id: number
  name: string
  icon: string
  category_type: 'expense' | 'income' | 'transfer'
  color: string | null
  active: boolean
}

export function useCategories() {
  const { apiFetch } = useApi()
  const { addToast } = useToast()
  const categories = useState<Category[]>('categories', () => [])
  const isLoading = ref(false)

  async function fetchCategories() {
    isLoading.value = true
    try {
      categories.value = await apiFetch<Category[]>('/api/v1/categories')
    } finally {
      isLoading.value = false
    }
  }

  async function createCategory(payload: Partial<Category>) {
    const data = await apiFetch<Category>('/api/v1/categories', {
      method: 'POST',
      body: payload,
    })
    categories.value = [...categories.value, data]
    addToast('Categoria criada', 'ok')
    return data
  }

  async function deleteCategory(id: number) {
    await apiFetch(`/api/v1/categories/${id}`, { method: 'DELETE' })
    categories.value = categories.value.filter((c) => c.id !== id)
    addToast('Categoria removida', 'ok')
  }

  const expenses = computed(() => categories.value.filter((c) => c.category_type === 'expense'))
  const incomes = computed(() => categories.value.filter((c) => c.category_type === 'income'))

  return { categories, isLoading, fetchCategories, createCategory, deleteCategory, expenses, incomes }
}
