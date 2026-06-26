require "rails_helper"

RSpec.describe Account, type: :model do
  describe "associations" do
    it { is_expected.to belong_to(:user) }
  end

  describe "validations" do
    subject { build(:account) }

    it { is_expected.to validate_presence_of(:name) }
    it { is_expected.to validate_length_of(:name).is_at_most(100) }
    it { is_expected.to validate_inclusion_of(:account_type).in_array(Account::ACCOUNT_TYPES) }
    it { is_expected.to validate_numericality_of(:balance) }
    it { is_expected.to validate_presence_of(:currency) }
    it { is_expected.to validate_length_of(:currency).is_equal_to(3) }
  end

  describe "scopes" do
    let(:user) { create(:user) }
    let!(:active_account)   { create(:account, user: user, active: true) }
    let!(:inactive_account) { create(:account, :inactive, user: user) }

    it "active scope returns only active accounts" do
      expect(Account.active).to include(active_account)
      expect(Account.active).not_to include(inactive_account)
    end

    it "by_type scope filters by account_type" do
      cc = create(:account, :credit_card, user: user)
      expect(Account.by_type("credit_card")).to include(cc)
      expect(Account.by_type("credit_card")).not_to include(active_account)
    end
  end
end
