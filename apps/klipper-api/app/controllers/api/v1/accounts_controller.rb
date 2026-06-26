module Api
  module V1
    class AccountsController < BaseController
      before_action :set_account, only: %i[show update destroy]

      def index
        accounts = current_user.accounts.active.order(:name)
        render json: accounts
      end

      def show
        render json: @account
      end

      def create
        account = current_user.accounts.build(account_params)
        if account.save
          render json: account, status: :created
        else
          render json: { errors: account.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def update
        if @account.update(account_params)
          render json: @account
        else
          render json: { errors: @account.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def destroy
        @account.update!(active: false)
        head :no_content
      end

      private

      def set_account
        @account = current_user.accounts.find(params[:id])
      rescue ActiveRecord::RecordNotFound
        render_error("Conta não encontrada", status: :not_found)
      end

      def account_params
        params.permit(:name, :institution, :account_type, :balance, :currency)
      end
    end
  end
end
