require "rails_helper"

RSpec.describe Transaction, type: :model do
  describe "associations" do
    it { is_expected.to belong_to(:user) }
    it { is_expected.to belong_to(:account).optional }
    it { is_expected.to belong_to(:category).optional }
  end

  describe "validations" do
    subject { build(:transaction) }

    it { is_expected.to validate_presence_of(:description) }
    it { is_expected.to validate_length_of(:description).is_at_most(255) }
    it { is_expected.to validate_numericality_of(:amount).is_greater_than(0) }
    it { is_expected.to validate_inclusion_of(:transaction_type).in_array(Transaction::TRANSACTION_TYPES) }
    it { is_expected.to validate_presence_of(:occurred_on) }
  end

  describe "installment validation" do
    it "is valid without installment fields" do
      expect(build(:transaction)).to be_valid
    end

    it "is valid with both installment fields" do
      expect(build(:transaction, :with_installments)).to be_valid
    end

    it "is invalid with only installment_total" do
      t = build(:transaction, installment_total: 12, installment_number: nil)
      expect(t).not_to be_valid
    end

    it "is invalid when installment_number exceeds installment_total" do
      t = build(:transaction, installment_total: 3, installment_number: 5)
      expect(t).not_to be_valid
    end
  end

  describe "scopes" do
    let(:user)    { create(:user) }
    let(:account) { create(:account, user: user) }

    it "in_month returns transactions in the given month" do
      tx = create(:transaction, user: user, account: account,
        occurred_on: Date.new(2026, 6, 15))
      other = create(:transaction, user: user, account: account,
        occurred_on: Date.new(2026, 5, 15))

      expect(Transaction.in_month(2026, 6)).to include(tx)
      expect(Transaction.in_month(2026, 6)).not_to include(other)
    end
  end
end
