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

    # Regressão FIN-002: a venda entrava somando, e o snapshot persistido passava
    # a divergir do PortfolioService para qualquer usuário com venda registrada.
    it "subtracts sell operations from the investment cost" do
      user = create(:user)
      create(:account, user: user, balance: 1000)
      create(:investment, user: user, ticker: "IVVB11", quantity: 10, average_price: 100)
      create(:investment, :sell, user: user, ticker: "IVVB11", quantity: 4, average_price: 120)

      snapshot = described_class.call(user)

      expect(snapshot.investments_cost.to_f).to eq(520.0) # 1000 - 480, não 1480
      expect(snapshot.net_worth.to_f).to eq(1520.0)
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
