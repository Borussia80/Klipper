class RecordNetWorthSnapshotsJob < ApplicationJob
  queue_as :default

  def perform(at = Date.current)
    User.find_each do |user|
      NetWorthSnapshotService.call(user, at: at)
    rescue StandardError => e
      Rails.logger.error("Falha ao registrar snapshot patrimonial do usuário #{user.id}: #{e.message}")
    end
  end
end
