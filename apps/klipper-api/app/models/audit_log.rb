class AuditLog < ApplicationRecord
  belongs_to :user

  validates :event_type, presence: true
  validates :user_id, presence: true
  validates :record_count, presence: true, numericality: { greater_than_or_equal_to: 0 }
  validates :status, presence: true,
            inclusion: { in: %w[success failure] }
  validates :event_type, inclusion: { in: %w[IMPORT_DATA EXPORT_DATA] }

  scope :recent_first, -> { order(created_at: :desc) }

  before_destroy { raise ActiveRecord::ReadOnlyRecord, "AuditLog entries are immutable" }

  def readonly?
    persisted?
  end

  def import_data?
    event_type == "IMPORT_DATA"
  end

  def export_data?
    event_type == "EXPORT_DATA"
  end

  def success?
    status == "success"
  end

  def failure?
    status == "failure"
  end
end
