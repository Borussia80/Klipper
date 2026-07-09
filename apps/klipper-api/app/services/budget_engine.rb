class BudgetEngine
  def initialize(user, year, month)
    @user  = user
    @year  = year
    @month = month
  end

  def summary
    budgets = @user.budgets.for_period(@year, @month).includes(:category)
    budgets.map do |budget|
      spent = @user.transactions
        .where(category: budget.category, transaction_type: "debit")
        .in_month(@year, @month)
        .sum(:amount)

      remaining = budget.amount_limit - spent
      pct = budget.amount_limit.positive? ? (spent / budget.amount_limit * 100).round(1) : 0.0
      recurrence = CategoryRecurrenceCalculator.new(
        @user, budget.category, reference_date: Date.new(@year, @month, 1)
      ).call

      {
        budget_id:      budget.id,
        category_id:    budget.category_id,
        category_name:  budget.category.name,
        category_icon:  budget.category.icon,
        natureza:       budget.category.natureza,
        amount_limit:   budget.amount_limit.to_f.round(2),
        spent:          spent.to_f.round(2),
        remaining:      remaining.to_f.round(2),
        pct_used:       pct.to_f.round(1),
        recorrencia:    recurrence[:recorrencia],
        months_present: recurrence[:months_present],
        months_total:   recurrence[:months_total]
      }
    end
  end
end
