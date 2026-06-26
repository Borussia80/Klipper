require "rails_helper"

RSpec.describe Budget, type: :model do
  describe "associations" do
    it { is_expected.to belong_to(:user) }
    it { is_expected.to belong_to(:category) }
  end

  describe "validations" do
    subject { build(:budget) }

    it { is_expected.to validate_numericality_of(:amount_limit).is_greater_than(0) }
    it { is_expected.to validate_numericality_of(:period_month).is_in(1..12) }
  end

  describe "uniqueness per period" do
    let(:user)     { create(:user) }
    let(:category) { create(:category, user: user) }

    it "prevents duplicate budget for same category + period" do
      create(:budget, user: user, category: category, period_year: 2026, period_month: 6)
      dup = build(:budget, user: user, category: category, period_year: 2026, period_month: 6)
      expect(dup).not_to be_valid
    end

    it "allows same category in different months" do
      create(:budget, user: user, category: category, period_year: 2026, period_month: 6)
      other = build(:budget, user: user, category: category, period_year: 2026, period_month: 7)
      expect(other).to be_valid
    end
  end
end
