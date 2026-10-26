module Api
  module V1
    class TransfersController < BaseController
      def create
        result = TransferService.new(current_user, **transfer_attributes).create
        render json: { debit: result.debit, credit: result.credit }, status: :created
      rescue TransferService::InvalidTransfer, ActiveRecord::RecordInvalid => error
        render json: { errors: [ error.message ] }, status: :unprocessable_entity
      rescue ActiveRecord::RecordNotFound
        render_error("Conta inválida")
      end

      def update
        transaction = current_user.transactions.find(params[:id])
        result = TransferService.update(transaction, update_attributes)
        render json: { debit: result.debit, credit: result.credit }
      rescue TransferService::InvalidTransfer, ActiveRecord::RecordInvalid => error
        render json: { errors: [ error.message ] }, status: :unprocessable_entity
      rescue ActiveRecord::RecordNotFound
        render_error("Transferência não encontrada", status: :not_found)
      end

      private

      def transfer_attributes
        {
          source_account: current_user.accounts.find(params[:source_account_id]),
          destination_account: current_user.accounts.find(params[:destination_account_id]),
          amount: params[:amount], occurred_on: params[:occurred_on], description: params[:description],
          status: params[:status].presence || "efetivado"
        }
      end

      def update_attributes
        params.permit(:amount, :description, :occurred_on, :status).to_h.symbolize_keys
      end
    end
  end
end
