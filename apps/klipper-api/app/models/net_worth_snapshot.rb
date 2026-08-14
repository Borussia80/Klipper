class NetWorthSnapshot < ApplicationRecord
  belongs_to :user

  validates :year, :month, presence: true
  validates :month, inclusion: { in: 1..12 }
  validates :accounts_total, :investments_cost, :net_worth, numericality: true
  validates :year, uniqueness: { scope: [ :user_id, :month ] }

  scope :ordered, -> { order(:year, :month) }
end
