class Transaction < ApplicationRecord
  belongs_to :user
  belongs_to :account
  belongs_to :category, optional: true

  belongs_to :parent_transaction, class_name: "Transaction", optional: true
  has_many   :split_transactions, class_name: "Transaction",
    foreign_key: :parent_transaction_id, dependent: :nullify

  TRANSACTION_TYPES = %w[debit credit transfer].freeze

  validates :description, presence: true, length: { maximum: 255 }
  validates :amount, numericality: { greater_than: 0 }
  validates :transaction_type, inclusion: { in: TRANSACTION_TYPES }
  validates :occurred_on, presence: true
  validate  :installment_fields_consistent

  scope :debits,   -> { where(transaction_type: "debit") }
  scope :credits,  -> { where(transaction_type: "credit") }
  scope :in_month, ->(year, month) { where(occurred_on: Date.new(year, month).all_month) }

  private

  def installment_fields_consistent
    return if installment_total.blank? && installment_number.blank?
    if installment_total.blank? || installment_number.blank?
      errors.add(:base, "installment_total and installment_number must both be present")
    elsif installment_number > installment_total
      errors.add(:installment_number, "cannot exceed installment_total")
    end
  end
end
