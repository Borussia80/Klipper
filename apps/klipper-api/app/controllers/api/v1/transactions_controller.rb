module Api
  module V1
    class TransactionsController < BaseController
      before_action :set_transaction, only: %i[show update destroy]

      def index
        txns = current_user.transactions.includes(:account, :category)
        txns = txns.in_month(params[:year].to_i, params[:month].to_i) if params[:year] && params[:month]
        txns = txns.where(account_id: params[:account_id]) if params[:account_id]
        txns = txns.where(transaction_type: params[:type]) if params[:type]
        render json: txns.order(occurred_on: :desc, id: :desc)
      end

      def show
        render json: @transaction
      end

      def create
        txn = current_user.transactions.build(transaction_params)
        txn.account = current_user.accounts.find_by(id: txn.account_id)
        if txn.category_id.blank?
          auto = AutoCategorizerService.call(txn.description.to_s, current_user)
          txn.category = auto if auto
        end
        if txn.save
          render json: txn, status: :created
        else
          render json: { errors: txn.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def update
        if @transaction.update(transaction_params)
          render json: @transaction
        else
          render json: { errors: @transaction.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def destroy
        @transaction.destroy!
        head :no_content
      end

      private

      def set_transaction
        @transaction = current_user.transactions.find(params[:id])
      rescue ActiveRecord::RecordNotFound
        render_error("Lançamento não encontrado", status: :not_found)
      end

      def transaction_params
        params.permit(:account_id, :category_id, :description, :amount,
          :transaction_type, :occurred_on, :notes, :installment_total, :installment_number)
      end
    end
  end
end
