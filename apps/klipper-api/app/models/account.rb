class Account < ApplicationRecord
  belongs_to :user

  ACCOUNT_TYPES = %w[checking savings digital credit_card investment].freeze
  DEBT_FIELDS = %w[saldo_fatura_atual pagamento_minimo juros_rotativo_am juros_rotativo_aa iof_projetado].freeze

  validates :name, presence: true, length: { maximum: 100 }
  validates :account_type, inclusion: { in: ACCOUNT_TYPES }
  validates :balance, numericality: true
  validates :currency, presence: true, length: { is: 3 }
  validates :saldo_fatura_atual, :pagamento_minimo, :juros_rotativo_am, :juros_rotativo_aa, :iof_projetado,
            numericality: { greater_than_or_equal_to: 0 }, allow_nil: true

  before_save :touch_saldo_atualizado_em, if: :debt_fields_changed?

  scope :active, -> { where(active: true) }
  scope :by_type, ->(type) { where(account_type: type) }
  scope :with_debt_data, -> { where.not(saldo_fatura_atual: nil).where.not(juros_rotativo_am: nil) }

  private

  def debt_fields_changed?
    (changed & DEBT_FIELDS).any?
  end

  def touch_saldo_atualizado_em
    self.saldo_atualizado_em = Time.current
  end
end
