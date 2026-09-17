class ReimbursementCoverageCalculator
  DEFAULT_MONTHS = 6
  ALERT_RATIO = 0.5
  ALERT_WINDOW_MONTHS = 3

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
    # Sem teto em 100 de propósito: reembolso é lançado no mês em que o dinheiro
    # cai, não no mês do gasto que ele cobre, então 150% é o caso normal de um
    # reembolso atrasado entrando agora — informação que o usuário quer ver.
    # Limitar em 100 apagaria justamente esse sinal. nil quando não houve gasto,
    # porque aí a razão não existe (FIN-009).
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
      alert:               alert?
    }
  end

  private

  # `spent` e `reimbursed` confrontam débito e crédito da mesma competência, e o
  # convênio costuma pagar no mês seguinte ao do gasto: um pagamento atrasado tem
  # a mesma assinatura de uma glosa. O alerta então acumula — os meses recentes
  # contra os anteriores da janela, cada lado somado antes de virar razão, para
  # que um crédito que caiu fora do mês continue na conta. O preço é detectar uma
  # glosa real alguns meses mais tarde, quando ela já se sustenta.
  def alert?
    recent   = pooled_coverage(recent_months)
    baseline = pooled_coverage(baseline_months)
    return false if recent.nil? || baseline.nil?

    recent < baseline * ALERT_RATIO
  end

  # A razão do bloco inteiro, não a média das razões mensais: assim um mês sem
  # crédito nenhum não entra como um 0% que puxa a média sozinho.
  def pooled_coverage(months)
    spent = months.sum { |(y, m)| spent_in(y, m) }
    return nil unless spent.positive?

    months.sum { |(y, m)| reimbursed_in(y, m) } / spent * 100
  end

  def recent_months
    ref = @reference_date.to_date
    ([ [ ref.year, ref.month ] ] + historical_months).first(ALERT_WINDOW_MONTHS)
  end

  def baseline_months
    historical_months - recent_months
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
