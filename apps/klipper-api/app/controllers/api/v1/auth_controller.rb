module Api
  module V1
    class AuthController < ActionController::API
      include ActionController::Cookies
      # Comparação de senha em tempo constante mesmo quando o e-mail não existe,
      # pra não vazar (via latência) se um e-mail está cadastrado ou não.
      FAKE_PASSWORD_DIGEST = BCrypt::Password.create(SecureRandom.hex(32)).freeze

      def sign_up
        user = User.new(sign_up_params)
        if user.save
          DefaultCategoriesSeederService.call(user)
          token = issue_tokens(user)
          render json: { token: token, user: user_json(user) }, status: :created
        else
          render json: { errors: user.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def sign_in
        user = User.find_by(email: params[:email]&.downcase)
        authenticated = (user || User.new(password_digest: FAKE_PASSWORD_DIGEST)).authenticate(params[:password])

        if user && authenticated
          token = issue_tokens(user)
          render json: { token: token, user: user_json(user) }
        else
          render json: { error: "E-mail ou senha inválidos" }, status: :unauthorized
        end
      end

      def refresh
        decoded = JwtService.decode(cookies[:klipper_refresh])
        unless decoded && decoded[:token_type] == "refresh"
          return render json: { error: "Refresh token inválido" }, status: :unauthorized
        end

        user = User.find_by(id: decoded[:user_id])
        unless user && decoded[:token_version].to_i == user.token_version
          return render json: { error: "Refresh token inválido" }, status: :unauthorized
        end

        token = issue_tokens(user)
        render json: { token: token, user: user_json(user) }
      end

      private

      def sign_up_params
        params.permit(:email, :password, :password_confirmation, :name)
      end

      def user_json(user)
        { id: user.id, email: user.email, name: user.name }
      end

      def issue_tokens(user)
        refresh = JwtService.encode_refresh(user_id: user.id, token_version: user.token_version)
        cookies[:klipper_refresh] = {
          value: refresh,
          httponly: true,
          secure: Rails.env.production?,
          same_site: :lax,
          path: "/api/v1/auth",
          expires: 30.days.from_now
        }
        JwtService.encode(user_id: user.id, token_version: user.token_version)
      end
    end
  end
end
