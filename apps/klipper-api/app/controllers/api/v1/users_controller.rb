module Api
  module V1
    class UsersController < BaseController
      include ActionController::Cookies
      before_action :authenticate_request!
      after_action :log_export_audit_event, only: :export

      def me
        render json: user_json(@current_user), status: :ok
      end

      def export
        records = {
          accounts: @current_user.accounts.to_a,
          categories: @current_user.categories.to_a,
          transactions: @current_user.transactions.to_a,
          budgets: @current_user.budgets.to_a,
          investments: @current_user.investments.to_a,
          members: @current_user.members.to_a,
          net_worth_snapshots: @current_user.net_worth_snapshots.to_a
        }
        @export_record_count = records.values.sum(&:size)

        render json: records.transform_values { |rows| rows.map(&:serializable_hash) }.merge(user: user_json(@current_user))
      end

      def destroy
        unless @current_user.authenticate(params[:current_password])
          render json: { error: "Senha atual incorreta" }, status: :unprocessable_entity
          return
        end

        @current_user.destroy!
        cookies.delete(:klipper_refresh, path: "/api/v1/auth")
        head :no_content
      end

      def update
        if changing_email? && !@current_user.authenticate(params[:current_password])
          render json: { error: "Senha atual incorreta" }, status: :unprocessable_entity
          return
        end

        if @current_user.update(update_params)
          render json: user_json(@current_user), status: :ok
        else
          render json: { errors: @current_user.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def password
        unless @current_user.authenticate(params[:current_password])
          render json: { error: "Senha atual incorreta" }, status: :unprocessable_entity
          return
        end

        if params[:password] != params[:password_confirmation]
          render json: { error: "Confirmação de senha não confere" }, status: :unprocessable_entity
          return
        end

        if @current_user.update(password: params[:password], password_confirmation: params[:password_confirmation])
          @current_user.increment!(:token_version)
          render json: { message: "Senha alterada com sucesso" }, status: :ok
        else
          render json: { errors: @current_user.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def logout
        @current_user.increment!(:token_version)
        cookies.delete(:klipper_refresh, path: "/api/v1/auth")
        render json: { message: "Sessão encerrada" }, status: :ok
      end

      private

      def update_params
        params.permit(:name, :email)
      end

      def changing_email?
        update_params[:email].present? && update_params[:email] != @current_user.email
      end

      def user_json(user)
        { id: user.id, email: user.email, name: user.name, created_at: user.created_at }
      end

      def log_export_audit_event
        AuditLog.create!(
          user: @current_user,
          event_type: "EXPORT_DATA",
          status: "success",
          record_count: @export_record_count
        )
      end
    end
  end
end
