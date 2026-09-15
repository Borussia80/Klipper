class RecordNetWorthSnapshotsJob < ApplicationJob
  queue_as :default

  def perform(at = Date.current)
    User.find_each do |user|
      NetWorthSnapshotService.call(user, at: at)
    end
  end
end
