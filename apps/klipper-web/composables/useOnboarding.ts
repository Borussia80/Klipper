export interface OnboardingGoal {
  id: string
  icon: string
  label: string
}

export interface OnboardingInput {
  bankNames: string[]
  goal: OnboardingGoal | null
  savingsGoal: string
}

export function useOnboarding() {
  const { createAccount } = useAccounts()
  const { createCategory } = useCategories()
  const { createBudget } = useBudgets()

  async function completeOnboarding(input: OnboardingInput) {
    await Promise.all(
      input.bankNames.map((name) =>
        createAccount({ name, institution: name, account_type: 'checking', currency: 'BRL' })
      )
    )

    if (!input.goal) return

    const category = await createCategory({
      name: input.goal.label,
      icon: input.goal.icon,
      category_type: 'expense',
      natureza: 'fixo',
      color: '#6B93AE',
    })

    const amount = parseBRLAmount(input.savingsGoal)
    if (amount === null || amount <= 0) return

    const now = new Date()
    await createBudget({
      category_id: category.id,
      amount_limit: amount.toFixed(2),
      period_month: now.getMonth() + 1,
      period_year: now.getFullYear(),
    })
  }

  return { completeOnboarding }
}
