class Category < ApplicationRecord
  belongs_to :user
  belongs_to :reimbursed_by_category, class_name: "Category", optional: true
  has_many :reimbursed_expense_categories, class_name: "Category",
    foreign_key: :reimbursed_by_category_id, inverse_of: :reimbursed_by_category, dependent: :nullify

  CATEGORY_TYPES = %w[expense income transfer].freeze
  NATUREZAS = %w[fixo cartao_parcelamento variavel].freeze

  validates :name, presence: true, length: { maximum: 80 }
  validates :category_type, inclusion: { in: CATEGORY_TYPES }
  validates :natureza, inclusion: { in: NATUREZAS }
  validates :icon, presence: true
  validates :color, format: { with: /\A#[0-9A-Fa-f]{6}\z/, message: "must be a valid hex color" }, allow_blank: true
  validates :reimbursed_by_category_id, comparison: { other_than: :id, message: "não pode reembolsar a si mesma" }, allow_nil: true
  validate :reimbursed_by_category_must_be_valid

  scope :active,             -> { where(active: true) }
  scope :expenses,           -> { where(category_type: "expense") }
  scope :incomes,            -> { where(category_type: "income") }
  scope :fixo,               -> { where(natureza: "fixo") }
  scope :cartao_parcelamento, -> { where(natureza: "cartao_parcelamento") }
  scope :variavel,           -> { where(natureza: "variavel") }
  scope :with_reimbursement_link, -> { where.not(reimbursed_by_category_id: nil) }

  private

  def reimbursed_by_category_must_be_valid
    return unless reimbursed_by_category_id.present?

    errors.add(:reimbursed_by_category_id, "só pode ser definido em categorias de despesa") unless category_type == "expense"
    return unless reimbursed_by_category

    errors.add(:reimbursed_by_category, "deve ser uma categoria de receita") unless reimbursed_by_category.category_type == "income"
    errors.add(:reimbursed_by_category, "deve pertencer ao mesmo usuário") unless reimbursed_by_category.user_id == user_id
  end
end
