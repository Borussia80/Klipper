module Api
  module V1
    class BaseController < ApplicationController
      before_action :authenticate_request!

      private

      def authenticate_request!
        header = request.headers["Authorization"]
        token = header&.split(" ")&.last
        decoded = JwtService.decode(token)
        @current_user = User.find(decoded[:user_id]) if decoded
        render json: { error: "Não autorizado" }, status: :unauthorized unless @current_user
      rescue ActiveRecord::RecordNotFound
        render json: { error: "Usuário não encontrado" }, status: :unauthorized
      end

      def current_user
        @current_user
      end

      def render_error(message, status: :unprocessable_entity)
        render json: { error: message }, status: status
      end
    end
  end
end
