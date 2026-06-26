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
    it { is_expected.to validate_numericality_of(:quantity).is_greater_than_or_equal_to(0) }
    it { is_expected.to validate_numericality_of(:average_price).is_greater_than_or_equal_to(0) }
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
