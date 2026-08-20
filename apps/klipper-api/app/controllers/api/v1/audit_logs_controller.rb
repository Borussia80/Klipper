module Api
  module V1
    class AuditLogsController < BaseController
      def index
        logs = @current_user.audit_logs.recent_first
        render json: logs.map { |log|
          log.as_json(only: %i[id event_type status record_count checksum created_at])
             .merge("metadata" => log.metadata&.deep_stringify_keys)
        }
      end
    end
  end
end
