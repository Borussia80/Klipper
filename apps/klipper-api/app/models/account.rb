class Account < ApplicationRecord
  belongs_to :user
  has_many :transactions, dependent: :restrict_with_error

  ACCOUNT_TYPES = %w[checking savings digital credit_card investment].freeze
  DEBT_FIELDS = %w[saldo_fatura_atual pagamento_minimo juros_rotativo_am juros_rotativo_aa iof_projetado].freeze

  validates :name, presence: true, length: { maximum: 100 }
  validates :account_type, inclusion: { in: ACCOUNT_TYPES }
  validates :balance, numericality: true
  validates :opening_balance, numericality: true
  validates :opening_balance_on, presence: true
  validates :currency, presence: true, length: { is: 3 }
  validates :saldo_fatura_atual, :pagamento_minimo, :juros_rotativo_am, :juros_rotativo_aa, :iof_projetado,
            numericality: { greater_than_or_equal_to: 0 }, allow_nil: true

  before_validation :default_opening_balance_date, on: :create
  before_save :touch_saldo_atualizado_em, if: :debt_fields_changed?

  scope :active, -> { where(active: true) }
  scope :by_type, ->(type) { where(account_type: type) }
  scope :with_debt_data, -> { where.not(saldo_fatura_atual: nil).where.not(juros_rotativo_am: nil) }

  def balance_at(date)
    return nil if date < opening_balance_on

    movements = transactions.booked.kept.where("occurred_on <= ?", date).sum(&:ledger_delta)
    opening_balance + movements
  end

  def current_balance
    balance_at(Date.current)
  end

  private

  def debt_fields_changed?
    (changed & DEBT_FIELDS).any?
  end

  def touch_saldo_atualizado_em
    self.saldo_atualizado_em = Time.current
  end

  def default_opening_balance_date
    self.opening_balance_on ||= Date.current
    self.opening_balance = balance if balance_changed? && !opening_balance_changed?
  end
end
