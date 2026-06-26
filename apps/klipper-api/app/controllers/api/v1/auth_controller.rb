module Api
  module V1
    class AuthController < ActionController::API
      def sign_up
        user = User.new(sign_up_params)
        if user.save
          token = JwtService.encode(user_id: user.id)
          render json: { token: token, user: user_json(user) }, status: :created
        else
          render json: { errors: user.errors.full_messages }, status: :unprocessable_entity
        end
      end

      def sign_in
        user = User.find_by(email: params[:email]&.downcase)
        if user&.authenticate(params[:password])
          token = JwtService.encode(user_id: user.id)
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
