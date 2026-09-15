module Api
  module V1
    class ReportsController < BaseController
      after_action :log_export_audit_event, only: %i[
        monthly natureza_split reimbursement_coverage debt_ranking
        net_worth net_worth_history
      ]

      PERIOD_MONTHS = { "3m" => 3, "6m" => 6, "1a" => 12 }.freeze

      def monthly
        year  = params[:year]&.to_i  || Date.current.year
        month = params[:month]&.to_i || Date.current.month

        txns = @current_user.transactions.in_month(year, month)
        txns = txns.where(member_id: params[:member_id]) if params[:member_id]
        debits  = txns.where(transaction_type: "debit").sum(:amount)
        credits = txns.where(transaction_type: "credit").sum(:amount)

        # Três queries fixas — somas, contagens e as categorias de uma vez —
        # em vez de um `find_by` e um `count` por linha do agrupamento, que
        # faziam o custo subir junto com o número de categorias do usuário.
        debit_txns = txns.where(transaction_type: "debit")
        totals     = debit_txns.group(:category_id).sum(:amount)
        counts     = debit_txns.group(:category_id).count
        categories = @current_user.categories.where(id: totals.keys.compact).index_by(&:id)

        by_category = totals.map do |cat_id, total|
          cat = categories[cat_id]
          {
            category_id:   cat_id,
            category_name: cat&.name || "Sem categoria",
            category_icon: cat&.icon,
            total:         total.to_f.round(2),
            count:         counts[cat_id].to_i
          }
        end.sort_by { |r| -r[:total] }

        @export_record_count = txns.count

        render json: {
          year:          year,
          month:         month,
          total_debits:  debits.to_f.round(2),
          total_credits: credits.to_f.round(2),
          net:           (credits - debits).to_f.round(2),
          by_category:   by_category
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
            pct:      total.positive? ? (amount / total * 100).round(1) : 0.0
          }
        end

        @export_record_count = txns.count

        render json: {
          year:        year,
          month:       month,
          total:       total.to_f.round(2),
          by_natureza: by_natureza
        }
      end

      def reimbursement_coverage
        year  = params[:year]&.to_i  || Date.current.year
        month = params[:month]&.to_i || Date.current.month

        categories = @current_user.categories.expenses.active.with_reimbursement_link
          .includes(:reimbursed_by_category)
        categories = categories.where(id: params[:category_id]) if params[:category_id]

        # As somas da janela inteira saem de uma query só, compartilhada por
        # todas as categorias, em vez de duas por mês dentro de cada uma.
        reference_date = Date.new(year, month, 1)
        sums = ReimbursementCoverageCalculator.monthly_sums(
          @current_user, categories, reference_date: reference_date
        )

        rows = categories.map do |category|
          ReimbursementCoverageCalculator.new(
            @current_user, category, reference_date: reference_date, monthly_sums: sums
          ).call.merge(
            category_name: category.name,
            category_icon: category.icon,
            reimbursed_by_category_name: category.reimbursed_by_category.name,
          )
        end

        @export_record_count = rows.size

        render json: { year: year, month: month, categories: rows }
      end

      def debt_ranking
        ranking = DebtRankingCalculator.new(@current_user).ranking
        @export_record_count = ranking.size

        render json: { cards: ranking }
      end

      def net_worth
        accounts    = @current_user.accounts
        investments = @current_user.investments

        accounts_total   = accounts.sum(:balance).to_f.round(2)
        investments_cost = investments.sum("quantity * average_price").to_f.round(2)
        net_worth_value  = (accounts_total + investments_cost).round(2)

        by_type = investments.group(:investment_type)
          .sum("quantity * average_price")
          .map { |type, cost| { investment_type: type, total_cost: cost.to_f.round(2) } }
          .sort_by { |r| -r[:total_cost] }

        @export_record_count = accounts.count + investments.count

        render json: {
          accounts_total:      accounts_total,
          investments_cost:    investments_cost,
          net_worth:           net_worth_value,
          accounts:            accounts.map { |a| { id: a.id, name: a.name, balance: a.balance.to_f } },
          investments_by_type: by_type
        }
      end

      def net_worth_history
        snapshots = @current_user.net_worth_snapshots.ordered

        months = PERIOD_MONTHS[params[:period]]
        if months
          cutoff = Date.current.prev_month(months - 1)
          snapshots = snapshots.where(
            "(year * 12 + month) >= ?", cutoff.year * 12 + cutoff.month
          )
        end

        @export_record_count = snapshots.count

        render json: {
          period: params[:period] || "max",
          points: snapshots.map { |s| { year: s.year, month: s.month, net_worth: s.net_worth.to_f.round(2) } }
        }
      end

      private

      def log_export_audit_event
        AuditLog.create!(
          user: @current_user,
          event_type: "EXPORT_DATA",
          status: "success",
          record_count: @export_record_count || 0
        )
      end
    end
  end
end
