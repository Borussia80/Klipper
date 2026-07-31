require "rails_helper"

RSpec.describe NetWorthSnapshot, type: :model do
  describe "associations" do
    it { is_expected.to belong_to(:user) }
  end

  describe "validations" do
    subject { build(:net_worth_snapshot) }

    it { is_expected.to validate_presence_of(:year) }
    it { is_expected.to validate_presence_of(:month) }
    it { is_expected.to validate_inclusion_of(:month).in_range(1..12) }
    it { is_expected.to validate_numericality_of(:accounts_total) }
    it { is_expected.to validate_numericality_of(:investments_cost) }
    it { is_expected.to validate_numericality_of(:net_worth) }

    it "does not allow two snapshots for the same user/year/month" do
      user = create(:user)
      create(:net_worth_snapshot, user: user, year: 2026, month: 7)
      duplicate = build(:net_worth_snapshot, user: user, year: 2026, month: 7)

      expect(duplicate).not_to be_valid
    end

    it "allows the same year/month for different users" do
      create(:net_worth_snapshot, year: 2026, month: 7)
      other = build(:net_worth_snapshot, year: 2026, month: 7)

      expect(other).to be_valid
    end
  end

  describe ".ordered" do
    it "returns snapshots sorted chronologically" do
      user = create(:user)
      later  = create(:net_worth_snapshot, user: user, year: 2026, month: 6)
      sooner = create(:net_worth_snapshot, user: user, year: 2025, month: 12)

      expect(NetWorthSnapshot.ordered).to eq([ sooner, later ])
    end
  end
end
