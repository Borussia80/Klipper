class BudgetEngine
  def initialize(user, year, month)
    @user  = user
    @year  = year
    @month = month
  end

  # Categoria pai soma o que foi lançado nela e nas filhas; a filha, só o dela.
  # O limite da filha é um sub-envelope dentro do pai, não soma ao total — ver
  # #totals.
  def summary
    budgets.map do |budget|
      spent = spent_in(group_ids_for(budget.category))

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
        months_total:   recurrence[:months_total],
        children_over_parent: children_over_parent?(budget)
      }
    end
  end

  # Total do mês sem dupla contagem: cada grupo (raiz + filhas) entra uma vez.
  # Limite do grupo = o do pai, se houver; senão, a soma dos limites das filhas.
  # Gasto do grupo = todos os lançamentos do pai e das filhas, cada um uma vez.
  def totals
    groups = budgets.group_by { |b| b.category.parent_id || b.category_id }

    limit = groups.sum do |root_id, group|
      root_budget = group.find { |b| b.category_id == root_id }
      root_budget ? root_budget.amount_limit : group.sum(&:amount_limit)
    end
    spent = spent_in(groups.keys.flat_map { |root_id| [ root_id, *child_ids_of(root_id) ] })

    { amount_limit: limit.to_f.round(2), spent: spent.to_f.round(2) }
  end

  private

  def budgets
    @budgets ||= @user.budgets.for_period(@year, @month).includes(:category).to_a
  end

  def group_ids_for(category)
    [ category.id, *child_ids_of(category.id) ]
  end

  def child_ids_of(category_id)
    @child_ids ||= @user.categories.where.not(parent_id: nil).group_by(&:parent_id).transform_values { |cs| cs.map(&:id) }
    @child_ids.fetch(category_id, [])
  end

  def spent_in(category_ids)
    @user.transactions
      .where(category_id: category_ids, transaction_type: "debit")
      .in_month(@year, @month)
      .sum(:amount)
  end

  # Aviso, não bloqueio: os limites das subcategorias passam o da categoria.
  def children_over_parent?(budget)
    ids = child_ids_of(budget.category_id)
    return false if ids.empty?

    budgets.select { |b| ids.include?(b.category_id) }.sum(&:amount_limit) > budget.amount_limit
  end
end
