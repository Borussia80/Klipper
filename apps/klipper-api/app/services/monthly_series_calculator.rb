# A série mensal que o MonthlySummaryCalculator não dá: ele responde por um mês
# e a pergunta do painel é de tendência ("estou melhorando ou piorando?"), que
# precisa da janela inteira. Chamá-lo N vezes seria N idas ao banco; aqui a
# agregação por mês acontece no Postgres, em uma query só.
class MonthlySeriesCalculator
  DEFAULT_MONTHS = 6
  MAX_MONTHS = 24

  def initialize(user, year:, month:, months: DEFAULT_MONTHS, member_id: nil)
    @user = user
    @last_month = Date.new(year, month, 1)
    @months = months.to_i.clamp(1, MAX_MONTHS)
    @member_id = member_id
  end

  def call
    { points: window.map { |date| point(date) } }
  end

  # Fora do hash de `call` pelo mesmo motivo do MonthlySummaryCalculator: serve
  # ao log de auditoria de exportação, não ao contrato da resposta.
  def record_count
    transactions.count
  end

  private

  def window
    @window ||= (0...@months).map { |i| @last_month.prev_month(@months - 1 - i) }
  end

  def transactions
    @transactions ||= begin
      txns = @user.transactions.where(occurred_on: window.first..@last_month.end_of_month)
      @member_id ? txns.where(member_id: @member_id) : txns
    end
  end

  def totals
    @totals ||= transactions.group(
      Arel.sql("EXTRACT(YEAR FROM occurred_on)::int"),
      Arel.sql("EXTRACT(MONTH FROM occurred_on)::int"),
      :transaction_type
    ).sum(:amount)
  end

  # Mês sem lançamento vira ponto zerado: a série tem que ter um ponto por mês
  # da janela, senão o gráfico emenda dois meses distantes numa linha só.
  def point(date)
    credits = totals[[ date.year, date.month, "credit" ]] || 0
    debits  = totals[[ date.year, date.month, "debit" ]] || 0

    {
      year: date.year,
      month: date.month,
      total_credits: credits.to_f.round(2),
      total_debits: debits.to_f.round(2),
      net: (credits - debits).to_f.round(2)
    }
  end
end
