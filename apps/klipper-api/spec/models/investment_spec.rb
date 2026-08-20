require "rails_helper"

RSpec.describe Investment, type: :model do
  describe "associations" do
    it { is_expected.to belong_to(:user) }
    it { is_expected.to belong_to(:account).optional }
  end

  describe "validations" do
    subject { build(:investment) }

    it { is_expected.to validate_presence_of(:name) }
    it { is_expected.to validate_length_of(:name).is_at_most(100) }
    it { is_expected.to validate_inclusion_of(:investment_type).in_array(Investment::INVESTMENT_TYPES) }
    it { is_expected.to validate_inclusion_of(:operation_type).in_array(Investment::OPERATION_TYPES) }
    it { is_expected.to validate_numericality_of(:quantity).is_greater_than_or_equal_to(0) }
    it { is_expected.to validate_numericality_of(:average_price).is_greater_than_or_equal_to(0) }
  end

  describe "occurred_on default and future-date validation" do
    # A presença de occurred_on é validada no model, mas o before_validation abaixo
    # já preenche o valor com a data de hoje antes da validação rodar (mesmo default
    # que ModalNovoAporte.vue usa na UI) — por isso não há um cenário observável de
    # "nil passa despercebido", e o shoulda-matcher validate_presence_of não se aplica.
    it "defaults occurred_on to today when omitted" do
      investment = build(:investment, occurred_on: nil)
      investment.valid?
      expect(investment.occurred_on).to eq(Time.zone.today)
    end

    it "is invalid with a future occurred_on" do
      expect(build(:investment, occurred_on: Time.zone.today + 1)).not_to be_valid
    end

    it "is valid with occurred_on equal to today" do
      expect(build(:investment, occurred_on: Time.zone.today)).to be_valid
    end
  end

  describe "sufficient_quantity_for_sell" do
    let(:user) { create(:user) }

    it "is invalid selling a ticker with no prior position" do
      sell = build(:investment, :sell, user: user, ticker: "PETR4", quantity: 10)
      expect(sell).not_to be_valid
      expect(sell.errors[:quantity]).to be_present
    end

    it "is valid selling up to the held quantity" do
      create(:investment, user: user, ticker: "PETR4", quantity: 10)
      sell = build(:investment, :sell, user: user, ticker: "PETR4", quantity: 10)
      expect(sell).to be_valid
    end

    it "is invalid selling more than the held quantity" do
      create(:investment, user: user, ticker: "PETR4", quantity: 10)
      sell = build(:investment, :sell, user: user, ticker: "PETR4", quantity: 11)
      expect(sell).not_to be_valid
    end

    it "accounts for prior sells when computing the held position" do
      create(:investment, user: user, ticker: "PETR4", quantity: 10)
      create(:investment, :sell, user: user, ticker: "PETR4", quantity: 4)
      sell = build(:investment, :sell, user: user, ticker: "PETR4", quantity: 6)
      expect(sell).to be_valid

      too_much = build(:investment, :sell, user: user, ticker: "PETR4", quantity: 7)
      expect(too_much).not_to be_valid
    end
  end

  describe "#current_value" do
    let(:investment) { build(:investment, quantity: 10, average_price: 100) }

    it "calculates current value" do
      expect(investment.current_value(120)).to eq(1200)
    end
  end

  describe "#gain_loss" do
    let(:investment) { build(:investment, quantity: 10, average_price: 100) }

    it "returns positive gain" do
      expect(investment.gain_loss(120)).to eq(200)
    end

    it "returns negative loss" do
      expect(investment.gain_loss(80)).to eq(-200)
    end
  end
end
