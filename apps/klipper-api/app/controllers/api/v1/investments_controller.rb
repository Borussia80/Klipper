module Api
  module V1
    class InvestmentsController < BaseController
      before_action :set_investment, only: %i[show update destroy]

      def index
        investments = current_user.investments.includes(:account)
        investments = investments.by_type(params[:type]) if params[:type]
        render json: investments.order(:name)
      end

      def show
        render json: @investment
      end

      def portfolio
        render json: PortfolioService.new(current_user).totals
      end

      def create
        investment = current_user.investments.build(investment_params)
        if investment.save
          render json: investment, status: :created
        else
          render json: { errors: investment.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def update
        if @investment.update(investment_params)
          render json: @investment
        else
          render json: { errors: @investment.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def destroy
        @investment.destroy!
        head :no_content
      end

      private

      def set_investment
        @investment = current_user.investments.find(params[:id])
      rescue ActiveRecord::RecordNotFound
        render_error("Investimento não encontrado", status: :not_found)
      end

      def investment_params
        params.permit(:account_id, :ticker, :name, :investment_type,
          :quantity, :average_price, :currency)
      end
    end
  end
end
