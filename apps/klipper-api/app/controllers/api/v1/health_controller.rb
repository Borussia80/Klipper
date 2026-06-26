module Api
  module V1
    class HealthController < ActionController::API
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
