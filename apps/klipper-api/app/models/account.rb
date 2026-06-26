class Account < ApplicationRecord
  belongs_to :user

  ACCOUNT_TYPES = %w[checking savings digital credit_card investment].freeze

  validates :name, presence: true, length: { maximum: 100 }
  validates :account_type, inclusion: { in: ACCOUNT_TYPES }
  validates :balance, numericality: true
  validates :currency, presence: true, length: { is: 3 }

  scope :active, -> { where(active: true) }
  scope :by_type, ->(type) { where(account_type: type) }
end
