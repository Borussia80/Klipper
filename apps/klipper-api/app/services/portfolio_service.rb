class PortfolioService
  def initialize(user)
    @user = user
  end

  def allocation
    investments = @user.investments.group_by(&:investment_type)
    total_cost = @user.investments.sum { |i| i.quantity * i.average_price }

    investments.map do |type, group|
      type_cost = group.sum { |i| i.quantity * i.average_price }
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
    total_cost = investments.sum { |i| i.quantity * i.average_price }
    {
      total_positions: investments.count,
      total_cost:      total_cost.round(2),
      by_type:         allocation
    }
  end
end
