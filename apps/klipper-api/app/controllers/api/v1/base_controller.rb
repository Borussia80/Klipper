module Api
  module V1
    class BaseController < ApplicationController
      before_action :authenticate_request!

      private

      def authenticate_request!
        header = request.headers["Authorization"]
        token = header&.split(" ")&.last
        decoded = JwtService.decode(token)
        # O token_type é exigido aqui, e não só no /auth/refresh: sem isso o
        # refresh token (30 dias) autenticava em qualquer rota protegida, e o
        # teto de 15 minutos do access token valia só para quem o respeitasse.
        # A checagem é allowlist de propósito — um tipo novo emitido pelo
        # JwtService.encode no futuro é recusado até ser liberado de forma
        # explícita (ARCH-001).
        decoded = nil unless decoded && decoded[:token_type] == "access"
        user = User.find(decoded[:user_id]) if decoded
        @current_user = user if user && decoded[:token_version] == user.token_version
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
