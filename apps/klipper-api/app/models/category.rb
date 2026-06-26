class Category < ApplicationRecord
  belongs_to :user

  CATEGORY_TYPES = %w[expense income transfer].freeze

  validates :name, presence: true, length: { maximum: 80 }
  validates :category_type, inclusion: { in: CATEGORY_TYPES }
  validates :icon, presence: true
  validates :color, format: { with: /\A#[0-9A-Fa-f]{6}\z/, message: "must be a valid hex color" }, allow_blank: true

  scope :active,   -> { where(active: true) }
  scope :expenses, -> { where(category_type: "expense") }
  scope :incomes,  -> { where(category_type: "income") }
end
