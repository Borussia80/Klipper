module Api
  module V1
    class HealthController < ActionController::API
      # Render's health check prober hits the container directly, without going
      # through the edge TLS terminator, so config.force_ssl must not redirect it.
      SSL_REDIRECT_EXCLUDED_PATH = "/api/v1/health"

      def self.excluded_from_ssl_redirect?(request)
        request.path == SSL_REDIRECT_EXCLUDED_PATH
      end

      def index
        render json: {
          status: "ok",
          version: "1.0.0",
          env: Rails.env,
          timestamp: Time.current.iso8601
        }
      end
    end
  end
end
