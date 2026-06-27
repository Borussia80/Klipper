module Api
  module V1
    class ReportsController < BaseController
      def monthly
        year  = params[:year]&.to_i  || Date.current.year
        month = params[:month]&.to_i || Date.current.month

        txns = @current_user.transactions.in_month(year, month)
        debits  = txns.where(transaction_type: "debit").sum(:amount)
        credits = txns.where(transaction_type: "credit").sum(:amount)

        by_category = txns.where(transaction_type: "debit")
          .group(:category_id)
          .sum(:amount)
          .map do |cat_id, total|
            cat = cat_id ? @current_user.categories.find_by(id: cat_id) : nil
            {
              category_id:   cat_id,
              category_name: cat&.name || "Sem categoria",
              category_icon: cat&.icon,
              total:         total.to_f.round(2),
              count:         txns.where(transaction_type: "debit", category_id: cat_id).count,
            }
          end
          .sort_by { |r| -r[:total] }

        render json: {
          year:          year,
          month:         month,
          total_debits:  debits.to_f.round(2),
          total_credits: credits.to_f.round(2),
          net:           (credits - debits).to_f.round(2),
          by_category:   by_category,
        }
      end

      def net_worth
        accounts    = @current_user.accounts
        investments = @current_user.investments

        accounts_total   = accounts.sum(:balance).to_f.round(2)
        investments_cost = investments.sum("quantity * average_price").to_f.round(2)

        by_type = investments.group(:investment_type)
          .sum("quantity * average_price")
          .map { |type, cost| { investment_type: type, total_cost: cost.to_f.round(2) } }
          .sort_by { |r| -r[:total_cost] }

        render json: {
          accounts_total:      accounts_total,
          investments_cost:    investments_cost,
          net_worth:           (accounts_total + investments_cost).round(2),
          accounts:            accounts.map { |a| { id: a.id, name: a.name, balance: a.balance.to_f } },
          investments_by_type: by_type,
        }
      end
    end
  end
end
