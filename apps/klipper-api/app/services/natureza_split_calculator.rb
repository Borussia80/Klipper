# Divisão do gasto por natureza da categoria, extraída de
# ReportsController#natureza_split (ARCH-006).
#
# Itera Category::NATUREZAS, não as chaves do agrupamento: uma natureza sem
# nenhum lançamento no mês tem que aparecer com total 0,0 e pct 0,0, porque o
# gráfico do front espera as fatias todas. Iterar o resultado da query faria a
# fatia desaparecer em vez de aparecer zerada.
class NaturezaSplitCalculator
  def initialize(user, year:, month:, member_id: nil)
    @user = user
    @year = year
    @month = month
    @member_id = member_id
  end

  def call
    { total: total.to_f.round(2), by_natureza: by_natureza }
  end

  # Ver MonthlySummaryCalculator#record_count: serve ao log de auditoria, não
  # ao JSON da resposta.
  def record_count
    transactions.count
  end

  private

  def transactions
    @transactions ||= begin
      txns = @user.transactions.where(transaction_type: "debit").in_month(@year, @month)
      @member_id ? txns.where(member_id: @member_id) : txns
    end
  end

  def totals
    @totals ||= transactions.joins(:category).group("categories.natureza").sum(:amount)
  end

  def total
    @total ||= totals.values.sum
  end

  def by_natureza
    Category::NATUREZAS.map do |nat|
      amount = totals[nat] || 0
      {
        natureza: nat,
        total: amount.to_f.round(2),
        pct: total.positive? ? (amount / total * 100).round(1) : 0.0
      }
    end
  end
end
