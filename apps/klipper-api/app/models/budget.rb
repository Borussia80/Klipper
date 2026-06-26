class Budget < ApplicationRecord
  belongs_to :user
  belongs_to :category

  validates :amount_limit, numericality: { greater_than: 0 }
  validates :period_month, numericality: { in: 1..12 }
  validates :period_year,  numericality: { greater_than: 2000, less_than: 2100 }
  validates :category_id,  uniqueness: {
    scope: [ :user_id, :period_year, :period_month ],
    message: "already has a budget for this period"
  }

  scope :for_period, ->(year, month) { where(period_year: year, period_month: month) }
end
