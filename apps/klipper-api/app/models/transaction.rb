class Transaction < ApplicationRecord
  belongs_to :user
  belongs_to :account, optional: true
  belongs_to :category, optional: true
  belongs_to :member, optional: true

  belongs_to :parent_transaction, class_name: "Transaction", optional: true
  has_many   :split_transactions, class_name: "Transaction",
    foreign_key: :parent_transaction_id, dependent: :nullify

  TRANSACTION_TYPES = %w[debit credit transfer].freeze
  # O que o lançamento é (spec 03, L-1). Só regular e refund contam como receita
  # ou despesa; transferência, pagamento de fatura e ajuste só movem saldo.
  KINDS = %w[regular transfer refund adjustment card_payment].freeze
  COUNTABLE_KINDS = %w[regular refund].freeze
  STATUSES = %w[previsto efetivado conciliado].freeze
  # Conferido com o banco, o lançamento só muda de valor, data ou conta depois
  # de desconciliado (spec 02, C-9). Descrição, categoria e notas seguem livres.
  RECONCILED_LOCKED_FIELDS = %w[amount occurred_on account_id transaction_type kind].freeze

  validates :description, presence: true, length: { maximum: 255 }
  validates :amount, numericality: { greater_than: 0 }
  validates :transaction_type, inclusion: { in: TRANSACTION_TYPES }
  validates :occurred_on, presence: true
  validates :kind, inclusion: { in: KINDS }
  validates :status, inclusion: { in: STATUSES }
  validates :transaction_type, inclusion: { in: %w[credit], message: "de estorno deve ser crédito" }, if: -> { kind == "refund" }
  validate  :installment_fields_consistent
  validate  :occurred_on_not_in_future
  validate  :reconciled_entry_locked, on: :update

  # O formulário do front ainda envia transaction_type "transfer"; sem isto a
  # transferência voltaria a ser somada como receita ou despesa.
  before_validation { self.kind = "transfer" if transaction_type == "transfer" }

  scope :debits,   -> { where(transaction_type: "debit") }
  scope :credits,  -> { where(transaction_type: "credit") }
  scope :in_month, ->(year, month) { where(occurred_on: Date.new(year, month).all_month) }
  scope :kept, -> { where(deleted_at: nil) }
  scope :booked, -> { where.not(status: "previsto") }

  # Única definição do que entra em receita e despesa (spec 03, L-3 a L-6).
  # Todo calculator parte destes scopes; nenhum filtra transaction_type sozinho.
  scope :countable,       -> { kept.booked.where(kind: COUNTABLE_KINDS) }
  scope :income_entries,  -> { countable.where(kind: "regular", transaction_type: "credit") }
  scope :expense_entries, -> { countable.where(kind: "regular", transaction_type: "debit") }
  scope :refund_entries,  -> { countable.where(kind: "refund") }

  def ledger_delta
    transaction_type == "credit" ? amount : -amount
  end

  def debit?
    transaction_type == "debit"
  end

  def credit?
    transaction_type == "credit"
  end

  private

  def installment_fields_consistent
    return if installment_total.blank? && installment_number.blank?
    if installment_total.blank? || installment_number.blank?
      errors.add(:base, "installment_total and installment_number must both be present")
    elsif installment_number > installment_total
      errors.add(:installment_number, "cannot exceed installment_total")
    end
  end

  def reconciled_entry_locked
    return unless status_in_database == "conciliado"
    return if (RECONCILED_LOCKED_FIELDS & changed_attribute_names_to_save).empty?

    errors.add(:base, "Lançamento conciliado: desconcilie antes de alterar valor, data, conta ou tipo")
  end

  def occurred_on_not_in_future
    return if occurred_on.blank?
    errors.add(:occurred_on, "não pode ser uma data futura") if occurred_on > Time.zone.today
  end
end
