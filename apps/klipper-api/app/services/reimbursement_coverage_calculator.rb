class ReimbursementCoverageCalculator
  DEFAULT_MONTHS = 6
  ALERT_RATIO = 0.5

  # Soma, numa query só, débitos e créditos de todas as categorias envolvidas
  # ao longo de toda a janela. Quem calcula várias categorias monta isto uma
  # vez e repassa via `monthly_sums:` — sem isso cada instância refaz duas
  # queries por mês, 14 por categoria na janela padrão.
  #
  # A chave é [category_id, transaction_type, ano, mês]. Quem repassa o
  # resultado precisa tê-lo montado com o mesmo `months:`/`reference_date:` das
  # instâncias: uma janela menor não levanta erro, devolve zero para os meses
  # que ficaram de fora.
  def self.monthly_sums(user, categories, months: DEFAULT_MONTHS, reference_date: Date.current)
    ids = Array(categories).flat_map { |c| [ c.id, c.reimbursed_by_category_id ] }.compact.uniq
    return {} if ids.empty?

    ref = reference_date.to_date
    window = ref.prev_month(months).beginning_of_month..ref.end_of_month

    user.transactions
      .where(category_id: ids, occurred_on: window)
      .group(
        :category_id,
        :transaction_type,
        Arel.sql("EXTRACT(YEAR FROM occurred_on)::int"),
        Arel.sql("EXTRACT(MONTH FROM occurred_on)::int")
      )
      .sum(:amount)
  end

  def initialize(user, expense_category, months: DEFAULT_MONTHS, reference_date: Date.current,
                 monthly_sums: nil)
    @user = user
    @expense_category = expense_category
    @months = months
    @reference_date = reference_date
    @monthly_sums = monthly_sums
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

  # Chamado sozinho, o calculator ainda monta o próprio conjunto — só que numa
  # query em vez de duas por mês.
  def monthly_sums
    @monthly_sums ||= self.class.monthly_sums(
      @user, [ @expense_category ], months: @months, reference_date: @reference_date
    )
  end

  def spent_in(year, month)
    monthly_sums[[ @expense_category.id, "debit", year, month ]] || 0
  end

  def reimbursed_in(year, month)
    monthly_sums[[ @expense_category.reimbursed_by_category_id, "credit", year, month ]] || 0
  end

  def historical_months
    (1..@months).map do |i|
      d = @reference_date.to_date.prev_month(i)
      [ d.year, d.month ]
    end
  end
end
