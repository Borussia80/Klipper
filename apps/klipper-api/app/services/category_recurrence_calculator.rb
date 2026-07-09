class CategoryRecurrenceCalculator
  DEFAULT_MONTHS = 6

  RECORRENCIAS = %w[rotineiro ocasional pontual].freeze

  def initialize(user, category, months: DEFAULT_MONTHS, reference_date: Date.current)
    @user = user
    @category = category
    @months = months
    @reference_date = reference_date
  end

  def call
    present = months_present
    ratio = @months.positive? ? present.to_f / @months : 0.0

    {
      category_id: @category.id,
      months_present: present,
      months_total: @months,
      ratio: ratio.round(3),
      recorrencia: classify(ratio)
    }
  end

  private

  def classify(ratio)
    return "rotineiro" if ratio >= 0.6
    return "ocasional" if ratio >= 0.3
    "pontual"
  end

  def months_present
    reference_months.count do |(year, month)|
      @user.transactions
        .where(category_id: @category.id, transaction_type: "debit")
        .in_month(year, month)
        .exists?
    end
  end

  def reference_months
    (0...@months).map do |i|
      d = @reference_date.to_date.prev_month(i)
      [ d.year, d.month ]
    end
  end
end
