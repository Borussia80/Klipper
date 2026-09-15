module Api
  module V1
    class TransactionsController < BaseController
      PER_PAGE_DEFAULT = 50
      PER_PAGE_MAX = 200

      before_action :set_transaction, only: %i[show update destroy]

      def index
        txns = current_user.transactions.includes(:account, :category)
        txns = txns.in_month(params[:year].to_i, params[:month].to_i) if params[:year] && params[:month]
        txns = txns.where(account_id: params[:account_id]) if params[:account_id]
        txns = txns.where(member_id: params[:member_id]) if params[:member_id]
        txns = txns.where(transaction_type: params[:type]) if params[:type]
        return unless valid_cursor?

        render json: paginate_by_cursor(txns.order(occurred_on: :desc, id: :desc))
      end

      def valid_cursor?
        return true unless params[:cursor].present?

        decode_cursor(params[:cursor])
        true
      rescue ArgumentError
        render_error("Cursor inválido", status: :bad_request)
        false
      end
      private :valid_cursor?

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

      # O cursor carrega a última chave da ordenação (data + id). Assim, novos
      # lançamentos não deslocam a próxima página nem fazem um registro repetir.
      # O corpo continua sendo um array para preservar o contrato existente.
      def paginate_by_cursor(scope)
        per_page = params[:per_page].to_i
        per_page = per_page.positive? ? [ per_page, PER_PAGE_MAX ].min : PER_PAGE_DEFAULT

        if params[:cursor].present?
          occurred_on, id = decode_cursor(params[:cursor])
          scope = scope.where(
            "occurred_on < :date OR (occurred_on = :date AND id < :id)",
            date: occurred_on, id: id
          )
        end

        rows = scope.limit(per_page + 1).to_a
        has_next = rows.length > per_page
        rows = rows.first(per_page)

        response.headers["X-Per-Page"] = per_page.to_s
        response.headers["X-Next-Cursor"] = has_next && rows.last ? encode_cursor(rows.last) : ""

        rows
      end

      def encode_cursor(transaction)
        Base64.urlsafe_encode64(
          "#{transaction.occurred_on.iso8601}|#{transaction.id}",
          padding: false
        )
      end

      def decode_cursor(cursor)
        raw = Base64.urlsafe_decode64(cursor.to_s)
        date, id = raw.split("|", 2)
        raise ArgumentError unless date.present? && id.to_i.positive?

        [ Date.iso8601(date), id.to_i ]
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
