class Member < ApplicationRecord
  belongs_to :user

  RELATIONSHIPS = %w[titular dependente].freeze

  validates :name, presence: true, length: { maximum: 100 }
  validates :relationship, inclusion: { in: RELATIONSHIPS }

  scope :active, -> { where(active: true) }
end
