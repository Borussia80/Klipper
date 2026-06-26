class Investment < ApplicationRecord
  belongs_to :user
  belongs_to :account, optional: true

  INVESTMENT_TYPES = %w[stock fii etf fixed_income crypto other].freeze

  validates :name,            presence: true, length: { maximum: 100 }
  validates :investment_type, inclusion: { in: INVESTMENT_TYPES }
  validates :quantity,        numericality: { greater_than_or_equal_to: 0 }
  validates :average_price,   numericality: { greater_than_or_equal_to: 0 }
  validates :currency,        presence: true, length: { is: 3 }

  scope :by_type, ->(type) { where(investment_type: type) }

  def current_value(current_price)
    quantity * current_price
  end

  def gain_loss(current_price)
    current_value(current_price) - (quantity * average_price)
  end
end
