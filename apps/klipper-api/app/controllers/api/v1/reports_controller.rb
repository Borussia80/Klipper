module Api
  module V1
    class ReportsController < BaseController
      after_action :log_export_audit_event, only: %i[
        monthly monthly_series natureza_split reimbursement_coverage debt_ranking
        net_worth net_worth_history
      ]

      PERIOD_MONTHS = { "3m" => 3, "6m" => 6, "1a" => 12 }.freeze

      def monthly
        year  = params[:year]&.to_i  || Date.current.year
        month = params[:month]&.to_i || Date.current.month

        calculator = MonthlySummaryCalculator.new(
          @current_user, year: year, month: month, member_id: params[:member_id]
        )
        summary = calculator.call
        @export_record_count = calculator.record_count

        render json: { year: year, month: month, **summary }
      end

      def monthly_series
        year  = params[:year]&.to_i  || Date.current.year
        month = params[:month]&.to_i || Date.current.month

        calculator = MonthlySeriesCalculator.new(
          @current_user,
          year: year,
          month: month,
          months: params[:months]&.to_i || MonthlySeriesCalculator::DEFAULT_MONTHS,
          member_id: params[:member_id]
        )
        series = calculator.call
        @export_record_count = calculator.record_count

        render json: series
      end

      def natureza_split
        year  = params[:year]&.to_i  || Date.current.year
        month = params[:month]&.to_i || Date.current.month

        calculator = NaturezaSplitCalculator.new(
          @current_user, year: year, month: month, member_id: params[:member_id]
        )
        split = calculator.call
        @export_record_count = calculator.record_count

        render json: { year: year, month: month, **split }
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

        totals = NetWorthSnapshotService.compute(@current_user)

        by_type = investments.group(:investment_type)
          .sum(Investment.signed_cost_sql)
          .map { |type, cost| { investment_type: type, total_cost: cost.to_f.round(2) } }
          .sort_by { |r| -r[:total_cost] }

        @export_record_count = accounts.count + investments.count

        render json: {
          **totals,
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
