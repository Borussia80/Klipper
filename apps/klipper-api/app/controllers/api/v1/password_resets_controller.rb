module Api
  module V1
    class PasswordResetsController < ActionController::API
      def create
        user = User.find_by(email: params[:email]&.downcase)
        if user
          token = user.generate_token_for(:password_reset)
          UserMailer.password_reset(user, token).deliver_now
        end

        # Always the same response, whether or not the e-mail exists, to avoid
        # leaking which addresses are registered.
        render json: { message: "Se o e-mail existir, enviaremos um link de redefinição." }, status: :ok
      end

      def update
        user = User.find_by_token_for(:password_reset, params[:token])

        if user.nil?
          render json: { error: "Link inválido ou expirado" }, status: :unprocessable_entity
        elsif user.update(password: params[:password], password_confirmation: params[:password_confirmation])
          user.increment!(:token_version)
          render json: { message: "Senha redefinida com sucesso" }, status: :ok
        else
          render json: { errors: user.errors.full_messages }, status: :unprocessable_entity
        end
      end
    end
  end
end
