class User < ApplicationRecord
  has_secure_password

  has_many :accounts,     dependent: :destroy
  has_many :categories,   dependent: :destroy
  has_many :transactions, dependent: :destroy
  has_many :budgets,      dependent: :destroy
  has_many :investments,  dependent: :destroy
  validates :email, presence: true, uniqueness: { case_sensitive: false }, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :password, length: { minimum: 8 }, allow_nil: true

  before_save { self.email = email.downcase }
end
