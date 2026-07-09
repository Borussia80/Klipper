class ReimbursementCoverageCalculator
  DEFAULT_MONTHS = 6
  ALERT_RATIO = 0.5

  def initialize(user, expense_category, months: DEFAULT_MONTHS, reference_date: Date.current)
    @user = user
    @expense_category = expense_category
    @months = months
    @reference_date = reference_date
  end

  def call
    return nil unless @expense_category.reimbursed_by_category_id.present?

    year  = @reference_date.year
    month = @reference_date.month

    spent      = spent_in(year, month)
    reimbursed = reimbursed_in(year, month)
    coverage_pct = spent.positive? ? (reimbursed / spent * 100).round(1) : nil

    historical_pcts = historical_months.filter_map do |(y, m)|
      historical_spent = spent_in(y, m)
      next if historical_spent.zero?
      (reimbursed_in(y, m) / historical_spent * 100)
    end
    historical_avg_pct = historical_pcts.any? ? (historical_pcts.sum / historical_pcts.size).round(1) : nil

    {
      category_id:        @expense_category.id,
      spent:               spent.to_f.round(2),
      reimbursed:          reimbursed.to_f.round(2),
      coverage_pct:        coverage_pct&.to_f&.round(1),
      historical_avg_pct:  historical_avg_pct&.to_f&.round(1),
      months_considered:   historical_pcts.size,
      alert:               alert?(coverage_pct, historical_avg_pct)
    }
  end

  private

  def alert?(coverage_pct, historical_avg_pct)
    return false if coverage_pct.nil? || historical_avg_pct.nil?
    coverage_pct < historical_avg_pct * ALERT_RATIO
  end

  def spent_in(year, month)
    @user.transactions
      .where(category_id: @expense_category.id)
      .debits
      .in_month(year, month)
      .sum(:amount)
  end

  def reimbursed_in(year, month)
    @user.transactions
      .where(category_id: @expense_category.reimbursed_by_category_id)
      .credits
      .in_month(year, month)
      .sum(:amount)
  end

  def historical_months
    (1..@months).map do |i|
      d = @reference_date.to_date.prev_month(i)
      [ d.year, d.month ]
    end
  end
end
