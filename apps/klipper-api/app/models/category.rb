class Category < ApplicationRecord
  belongs_to :user
  belongs_to :reimbursed_by_category, class_name: "Category", optional: true
  has_many :reimbursed_expense_categories, class_name: "Category",
    foreign_key: :reimbursed_by_category_id, inverse_of: :reimbursed_by_category, dependent: :nullify

  # Dois níveis: uma raiz e suas filhas. As regras de validação estão em
  # parent_must_be_valid; a herança de natureza, em inherit_from_parent.
  belongs_to :parent, class_name: "Category", optional: true, inverse_of: :children
  has_many :children, class_name: "Category", foreign_key: :parent_id, inverse_of: :parent
  belongs_to :merged_into, class_name: "Category", optional: true

  CATEGORY_TYPES = %w[expense income transfer].freeze
  NATUREZAS = %w[fixo cartao_parcelamento variavel].freeze

  validates :name, presence: true, length: { maximum: 80 }
  validates :category_type, inclusion: { in: CATEGORY_TYPES }
  validates :natureza, inclusion: { in: NATUREZAS }
  validates :icon, presence: true
  validates :color, format: { with: /\A#[0-9A-Fa-f]{6}\z/, message: "must be a valid hex color" }, allow_blank: true
  validates :reimbursed_by_category_id, comparison: { other_than: :id, message: "não pode reembolsar a si mesma" }, allow_nil: true
  validate :reimbursed_by_category_must_be_valid
  validate :parent_must_be_valid

  before_validation :inherit_from_parent
  before_destroy :keep_parent_with_children

  scope :active,             -> { where(active: true) }
  scope :expenses,           -> { where(category_type: "expense") }
  scope :incomes,            -> { where(category_type: "income") }
  scope :fixo,               -> { where(natureza: "fixo") }
  scope :cartao_parcelamento, -> { where(natureza: "cartao_parcelamento") }
  scope :variavel,           -> { where(natureza: "variavel") }
  scope :with_reimbursement_link, -> { where.not(reimbursed_by_category_id: nil) }
  scope :roots,              -> { where(parent_id: nil) }

  private

  # A filha pertence ao grupo do pai no orçamento e na divisão por natureza, então
  # a natureza vem dele. O tipo não é herdado: é validado, para que uma filha de
  # despesa nunca vire receita em silêncio por causa do pai escolhido.
  def inherit_from_parent
    self.natureza = parent.natureza if parent
  end

  def parent_must_be_valid
    return if parent_id.blank?

    if parent_id == id
      errors.add(:parent_id, "não pode ser a própria categoria")
      return
    end
    return unless parent

    errors.add(:parent_id, "deve pertencer ao mesmo usuário") unless parent.user_id == user_id
    errors.add(:parent_id, "deve ser do mesmo tipo") unless parent.category_type == category_type
    errors.add(:parent_id, "precisa ser uma categoria principal") if parent.parent_id.present?
    errors.add(:parent_id, "categoria com subcategorias não pode virar subcategoria") if persisted? && children.exists?
  end

  # Na exclusão do usuário (cascata) as filhas vão junto; fora dela, um pai com
  # filhas não pode sumir e deixá-las soltas.
  def keep_parent_with_children
    return if destroyed_by_association
    return unless children.exists?

    errors.add(:base, "categoria com subcategorias não pode ser excluída")
    throw :abort
  end

  def reimbursed_by_category_must_be_valid
    return unless reimbursed_by_category_id.present?

    errors.add(:reimbursed_by_category_id, "só pode ser definido em categorias de despesa") unless category_type == "expense"
    return unless reimbursed_by_category

    errors.add(:reimbursed_by_category, "deve ser uma categoria de receita") unless reimbursed_by_category.category_type == "income"
    errors.add(:reimbursed_by_category, "deve pertencer ao mesmo usuário") unless reimbursed_by_category.user_id == user_id
  end
end
