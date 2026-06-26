module Api
  module V1
    class BudgetsController < BaseController
      before_action :set_budget, only: %i[show update destroy]

      def index
        budgets = current_user.budgets.includes(:category)
        budgets = budgets.for_period(params[:year].to_i, params[:month].to_i) if params[:year] && params[:month]
        render json: budgets.order(:period_year, :period_month)
      end

      def show
        render json: @budget
      end

      def summary
        year  = params.fetch(:year,  Date.today.year).to_i
        month = params.fetch(:month, Date.today.month).to_i
        render json: BudgetEngine.new(current_user, year, month).summary
      end

      def create
        budget = current_user.budgets.build(budget_params)
        if budget.save
          render json: budget, status: :created
        else
          render json: { errors: budget.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def update
        if @budget.update(budget_params)
          render json: @budget
        else
          render json: { errors: @budget.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def destroy
        @budget.destroy!
        head :no_content
      end

      private

      def set_budget
        @budget = current_user.budgets.find(params[:id])
      rescue ActiveRecord::RecordNotFound
        render_error("Orçamento não encontrado", status: :not_found)
      end

      def budget_params
        params.permit(:category_id, :amount_limit, :period_month, :period_year)
      end
    end
  end
end
