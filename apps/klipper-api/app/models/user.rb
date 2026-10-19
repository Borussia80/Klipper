class User < ApplicationRecord
  has_secure_password

  generates_token_for :password_reset, expires_in: 30.minutes do
    password_salt&.last(10)
  end

  # A ordem importa na exclusão da conta: o Rails registra um before_destroy por
  # associação na ordem de declaração, e transactions/investments/budgets têm FK
  # para accounts, categories e members. Os filhos precisam morrer primeiro.
  has_many :transactions, dependent: :destroy
  has_many :investments,  dependent: :destroy
  has_many :budgets,      dependent: :destroy
  has_many :accounts,     dependent: :destroy
  has_many :categories,   dependent: :destroy
  has_many :members,      dependent: :destroy
  has_many :net_worth_snapshots, dependent: :destroy
  has_many :audit_logs, dependent: :delete_all
  validates :email, presence: true, uniqueness: { case_sensitive: false }, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :password, length: { minimum: 8 }, allow_nil: true
  validate :own_names_are_valid
  validates :own_cpf_mask, format: { with: /\A[\d.-]{1,12}\z/ }, allow_blank: true

  before_save { self.email = email.downcase }

  def own_identity
    return if own_names.blank?

    BankImport::OwnIdentity.new(names: own_names, cpf_mask: own_cpf_mask)
  end

  private

  def own_names_are_valid
    names = Array(own_names)
    errors.add(:own_names, "must contain at most 5 names") if names.size > 5
    errors.add(:own_names, "must contain strings up to 80 characters") if names.any? { |name| !name.is_a?(String) || name.length > 80 }
  end
end
