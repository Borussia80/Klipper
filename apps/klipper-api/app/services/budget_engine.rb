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

      {
        budget_id:     budget.id,
        category_id:   budget.category_id,
        category_name: budget.category.name,
        category_icon: budget.category.icon,
        amount_limit:  budget.amount_limit,
        spent:         spent,
        remaining:     remaining,
        pct_used:      pct
      }
    end
  end
end
