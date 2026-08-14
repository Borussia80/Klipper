module Api
  module V1
    class AuthController < ActionController::API
      # Comparação de senha em tempo constante mesmo quando o e-mail não existe,
      # pra não vazar (via latência) se um e-mail está cadastrado ou não.
      FAKE_PASSWORD_DIGEST = BCrypt::Password.create(SecureRandom.hex(32)).freeze

      def sign_up
        user = User.new(sign_up_params)
        if user.save
          DefaultCategoriesSeederService.call(user)
          token = JwtService.encode(user_id: user.id, token_version: user.token_version)
          render json: { token: token, user: user_json(user) }, status: :created
        else
          render json: { errors: user.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def sign_in
        user = User.find_by(email: params[:email]&.downcase)
        authenticated = (user || User.new(password_digest: FAKE_PASSWORD_DIGEST)).authenticate(params[:password])

        if user && authenticated
          token = JwtService.encode(user_id: user.id, token_version: user.token_version)
          render json: { token: token, user: user_json(user) }
        else
          render json: { error: "E-mail ou senha inválidos" }, status: :unauthorized
        end
      end

      private

      def sign_up_params
        params.permit(:email, :password, :password_confirmation, :name)
      end

      def user_json(user)
        { id: user.id, email: user.email, name: user.name }
      end
    end
  end
end
