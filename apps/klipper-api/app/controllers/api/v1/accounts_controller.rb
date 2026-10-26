module Api
  module V1
    class AccountsController < BaseController
      before_action :set_account, only: %i[show update destroy balance_history]

      def index
        accounts = current_user.accounts.active.order(:name)
        render json: accounts.map { |account| account_json(account) }
      end

      def show
        render json: account_json(@account)
      end

      def create
        account = current_user.accounts.build(account_params)
        if account.save
          render json: account_json(account), status: :created
        else
          render json: { errors: account.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def update
        if @account.update(account_params)
          render json: account_json(@account)
        else
          render json: { errors: @account.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def destroy
        @account.update!(active: false)
        head :no_content
      end

      def balance_history
        from = parse_date(params[:from]) || @account.opening_balance_on
        to = parse_date(params[:to]) || Date.current
        return render_error("Período inválido") if from > to

        history = AccountBalanceHistory.new(@account, from: from, to: to).call
        render json: history.merge(from: from, to: to, account: account_json(@account))
      rescue Date::Error
        render_error("Data inválida")
      end

      private

      def set_account
        @account = current_user.accounts.find(params[:id])
      rescue ActiveRecord::RecordNotFound
        render_error("Conta não encontrada", status: :not_found)
      end

      def account_params
        params.permit(:name, :institution, :account_type, :balance, :currency, :opening_balance, :opening_balance_on,
                      :saldo_fatura_atual, :pagamento_minimo, :juros_rotativo_am,
                      :juros_rotativo_aa, :iof_projetado)
      end

      def account_json(account)
        account.as_json.merge(
          "balance" => account.current_balance.to_s("F"),
          "opening_balance" => account.opening_balance.to_s("F"),
          "opening_balance_on" => account.opening_balance_on
        )
      end

      def parse_date(value)
        Date.iso8601(value) if value.present?
      end
    end
  end
end
