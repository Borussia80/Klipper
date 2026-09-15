require "rails_helper"

RSpec.describe NetWorthSnapshotService do
  describe ".call" do
    it "upserts the current month's snapshot from accounts and investments" do
      user = create(:user)
      create(:account, user: user, balance: 3000)
      create(:investment, user: user, quantity: 2, average_price: 500)

      expect {
        described_class.call(user)
      }.to change { user.net_worth_snapshots.count }.from(0).to(1)

      snapshot = user.net_worth_snapshots.find_by(year: Date.current.year, month: Date.current.month)
      expect(snapshot.net_worth.to_f).to eq(4000.0)
    end

    it "updates the existing snapshot instead of creating a duplicate" do
      user = create(:user)
      create(:net_worth_snapshot, user: user, year: Date.current.year, month: Date.current.month)
      create(:account, user: user, balance: 2500)

      expect {
        described_class.call(user)
      }.not_to change { user.net_worth_snapshots.count }

      expect(user.net_worth_snapshots.find_by(year: Date.current.year, month: Date.current.month).net_worth.to_f)
        .to eq(2500.0)
    end
  end
end
