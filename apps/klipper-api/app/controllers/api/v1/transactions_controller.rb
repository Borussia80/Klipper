module Api
  module V1
    class TransactionsController < BaseController
      PER_PAGE_DEFAULT = 100
      PER_PAGE_MAX = 200

      before_action :set_transaction, only: %i[show update destroy]

      def index
        txns = current_user.transactions.includes(:account, :category)
        txns = txns.in_month(params[:year].to_i, params[:month].to_i) if params[:year] && params[:month]
        txns = txns.where(account_id: params[:account_id]) if params[:account_id]
        txns = txns.where(member_id: params[:member_id]) if params[:member_id]
        txns = txns.where(transaction_type: params[:type]) if params[:type]
        render json: paginate(txns.order(occurred_on: :desc, id: :desc))
      end

      def show
        render json: @transaction
      end

      def create
        unless valid_transaction_fks?
          return render json: { errors: [ "Conta, categoria ou portador inválido" ] }, status: :unprocessable_entity
        end

        txn = current_user.transactions.build(transaction_params)
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
        unless valid_transaction_fks?
          return render json: { errors: [ "Conta, categoria ou portador inválido" ] }, status: :unprocessable_entity
        end

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

      # O recorte vai em headers e o corpo continua sendo o array puro: um
      # envelope mudaria o contrato de `index` para todo cliente já existente.
      # `page`/`per_page` vêm do cliente, então ambos são saneados aqui — sem
      # teto, `per_page` grande desfaz a proteção que a paginação existe pra dar,
      # e `page` não-positivo viraria offset negativo.
      def paginate(scope)
        per_page = params[:per_page].to_i
        per_page = per_page.positive? ? [ per_page, PER_PAGE_MAX ].min : PER_PAGE_DEFAULT

        page = params[:page].to_i
        page = 1 unless page.positive?

        total = scope.count

        response.headers["X-Total-Count"] = total.to_s
        response.headers["X-Page"] = page.to_s
        response.headers["X-Per-Page"] = per_page.to_s
        response.headers["X-Total-Pages"] = (total.to_f / per_page).ceil.to_s

        scope.limit(per_page).offset((page - 1) * per_page)
      end

      def set_transaction
        @transaction = current_user.transactions.find(params[:id])
      rescue ActiveRecord::RecordNotFound
        render_error("Lançamento não encontrado", status: :not_found)
      end

      def transaction_params
        params.permit(:account_id, :category_id, :member_id, :description, :amount,
          :transaction_type, :occurred_on, :notes, :installment_total, :installment_number)
      end


      def valid_transaction_fks?
        return false if transaction_params[:account_id].present? &&
          !current_user.accounts.exists?(id: transaction_params[:account_id])
        return false if transaction_params[:category_id].present? &&
          !current_user.categories.exists?(id: transaction_params[:category_id])
        return false if transaction_params[:member_id].present? &&
          !current_user.members.exists?(id: transaction_params[:member_id])

        true
      end
    end
  end
end
