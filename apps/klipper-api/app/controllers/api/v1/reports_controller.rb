module Api
  module V1
    class ReportsController < BaseController
      def monthly
        year  = params[:year]&.to_i  || Date.current.year
        month = params[:month]&.to_i || Date.current.month

        txns = @current_user.transactions.in_month(year, month)
        txns = txns.where(member_id: params[:member_id]) if params[:member_id]
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

      def natureza_split
        year  = params[:year]&.to_i  || Date.current.year
        month = params[:month]&.to_i || Date.current.month

        txns = @current_user.transactions.where(transaction_type: "debit").in_month(year, month)
        txns = txns.where(member_id: params[:member_id]) if params[:member_id]

        totals = txns.joins(:category).group("categories.natureza").sum(:amount)
        total  = totals.values.sum

        by_natureza = Category::NATUREZAS.map do |nat|
          amount = totals[nat] || 0
          {
            natureza: nat,
            total:    amount.to_f.round(2),
            pct:      total.positive? ? (amount / total * 100).round(1) : 0.0,
          }
        end

        render json: {
          year:        year,
          month:       month,
          total:       total.to_f.round(2),
          by_natureza: by_natureza,
        }
      end

      def reimbursement_coverage
        year  = params[:year]&.to_i  || Date.current.year
        month = params[:month]&.to_i || Date.current.month

        categories = @current_user.categories.expenses.active.with_reimbursement_link
        categories = categories.where(id: params[:category_id]) if params[:category_id]

        rows = categories.map do |category|
          ReimbursementCoverageCalculator.new(
            @current_user, category, reference_date: Date.new(year, month, 1)
          ).call.merge(
            category_name: category.name,
            category_icon: category.icon,
            reimbursed_by_category_name: category.reimbursed_by_category.name,
          )
        end

        render json: { year: year, month: month, categories: rows }
      end

      def debt_ranking
        render json: { cards: DebtRankingCalculator.new(@current_user).ranking }
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
