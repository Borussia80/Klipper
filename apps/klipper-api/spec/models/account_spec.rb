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
    it { is_expected.to validate_numericality_of(:saldo_fatura_atual).is_greater_than_or_equal_to(0).allow_nil }
    it { is_expected.to validate_numericality_of(:pagamento_minimo).is_greater_than_or_equal_to(0).allow_nil }
    it { is_expected.to validate_numericality_of(:juros_rotativo_am).is_greater_than_or_equal_to(0).allow_nil }
    it { is_expected.to validate_numericality_of(:juros_rotativo_aa).is_greater_than_or_equal_to(0).allow_nil }
    it { is_expected.to validate_numericality_of(:iof_projetado).is_greater_than_or_equal_to(0).allow_nil }
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

    it "with_debt_data scope returns only cards with saldo and juros preenchidos" do
      complete = create(:account, :with_debt_data, user: user)
      incomplete = create(:account, :credit_card, user: user, saldo_fatura_atual: 100)
      expect(Account.with_debt_data).to include(complete)
      expect(Account.with_debt_data).not_to include(incomplete, active_account)
    end
  end

  describe "#saldo_atualizado_em" do
    let(:account) { create(:account, :with_debt_data) }

    it "is set on create when debt fields are present" do
      expect(account.saldo_atualizado_em).to be_present
    end

    it "updates when a debt field changes" do
      expect { account.update!(saldo_fatura_atual: 1000) }
        .to change(account, :saldo_atualizado_em)
    end

    it "does not change when an unrelated field changes" do
      expect { account.update!(name: "Novo nome") }
        .not_to change(account, :saldo_atualizado_em)
    end
  end
end
