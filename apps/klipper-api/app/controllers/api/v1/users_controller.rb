module Api
  module V1
    class UsersController < BaseController
      before_action :authenticate_request!

      def me
        render json: user_json(@current_user), status: :ok
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
    end
  end
end
