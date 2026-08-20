# total_cost é custo líquido da posição (buy soma, sell subtrai), NÃO valor de mercado —
# o sistema não tem cotação ao vivo em lugar nenhum hoje. allocation quebra esse mesmo
# custo líquido por investment_type; pct_of_portfolio é a fatia de cada tipo sobre o
# total_cost, não uma alocação por valor de mercado. Ver comentário em app/models/investment.rb.
class PortfolioService
  def initialize(user)
    @user = user
  end

  def allocation
    investments = @user.investments.group_by(&:investment_type)
    total_cost = @user.investments.sum { |i| signed_cost(i) }

    investments.map do |type, group|
      type_cost = group.sum { |i| signed_cost(i) }
      pct = total_cost.positive? ? (type_cost / total_cost * 100).round(1) : 0.0
      {
        investment_type: type,
        count:           group.size,
        total_cost:      type_cost.round(2),
        pct_of_portfolio: pct
      }
    end.sort_by { |r| -r[:total_cost] }
  end

  def totals
    investments = @user.investments
    total_cost = investments.sum { |i| signed_cost(i) }
    {
      total_positions: investments.count,
      total_cost:      total_cost.round(2),
      by_type:         allocation
    }
  end

  private

  def signed_cost(investment)
    cost = investment.quantity * investment.average_price
    investment.operation_type == "sell" ? -cost : cost
  end
end
