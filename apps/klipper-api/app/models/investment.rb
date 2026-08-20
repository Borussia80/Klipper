# Cada linha é uma operação isolada de um ledger (não um saldo agregado):
#   quantity       — unidades transacionadas NESTA linha.
#   average_price  — preço unitário DESTA linha. O nome é legado de corretora; não existe
#                     em nenhum lugar do código uma média ponderada entre linhas.
#   operation_type — buy soma, sell subtrai quantidade/custo na agregação (PortfolioService).
#   occurred_on    — data em que a operação ocorreu (não a data de criação do registro).
# "Posição" (quantidade líquida de um ticker) e "valor de mercado" NÃO são colunas: a
# primeira é calculada em #sufficient_quantity_for_sell abaixo; a segunda não existe em
# lugar nenhum do sistema hoje (current_value/gain_loss dependem de um current_price
# externo que nenhum controller/service fornece).
class Investment < ApplicationRecord
  belongs_to :user
  belongs_to :account, optional: true

  INVESTMENT_TYPES = %w[stock fii etf fixed_income crypto other].freeze
  OPERATION_TYPES = %w[buy sell].freeze

  before_validation :default_occurred_on, on: :create

  validates :name,            presence: true, length: { maximum: 100 }
  validates :investment_type, inclusion: { in: INVESTMENT_TYPES }
  validates :operation_type,  inclusion: { in: OPERATION_TYPES }
  validates :quantity,        numericality: { greater_than_or_equal_to: 0 }
  validates :average_price,   numericality: { greater_than_or_equal_to: 0 }
  validates :currency,        presence: true, length: { is: 3 }
  validates :occurred_on,     presence: true
  validate  :occurred_on_not_in_future
  validate  :sufficient_quantity_for_sell, if: -> { operation_type == "sell" }

  scope :by_type, ->(type) { where(investment_type: type) }

  def current_value(current_price)
    quantity * current_price
  end

  def gain_loss(current_price)
    current_value(current_price) - (quantity * average_price)
  end

  private

  def default_occurred_on
    self.occurred_on ||= Time.zone.today
  end

  def occurred_on_not_in_future
    return if occurred_on.blank?
    errors.add(:occurred_on, "não pode ser uma data futura") if occurred_on > Time.zone.today
  end

  # Posição líquida de um ticker = soma sinalizada de quantity (buy soma, sell subtrai)
  # entre as linhas do mesmo user_id + ticker, ignorando account_id (hoje não há vínculo
  # consistente conta↔posição — ver auditoria de superfícies financeiras).
  def sufficient_quantity_for_sell
    return if ticker.blank? || user_id.blank?

    held = Investment.where(user_id: user_id, ticker: ticker)
      .where.not(id: id)
      .sum { |i| i.operation_type == "sell" ? -i.quantity : i.quantity }

    if quantity > held
      errors.add(:quantity, "insuficiente para venda (posição atual: #{held})")
    end
  end
end
