require "rails_helper"

RSpec.describe NetWorthSnapshotService do
  describe ".compute" do
    it "returns the three totals without persisting a snapshot" do
      user = create(:user)
      create(:account, user: user, balance: 3000)
      create(:investment, user: user, quantity: 2, average_price: 500)

      expect(described_class.compute(user))
        .to eq(accounts_total: 3000.0, investments_cost: 1000.0, net_worth: 4000.0)
      expect(user.net_worth_snapshots.count).to eq(0)
    end

    it "subtracts sell operations from the investment cost" do
      user = create(:user)
      create(:account, user: user, balance: 1000)
      create(:investment, user: user, ticker: "IVVB11", quantity: 10, average_price: 100)
      create(:investment, :sell, user: user, ticker: "IVVB11", quantity: 4, average_price: 120)

      expect(described_class.compute(user))
        .to eq(accounts_total: 1000.0, investments_cost: 520.0, net_worth: 1520.0)
    end

    it "returns zeros for a user with no accounts and no investments" do
      expect(described_class.compute(create(:user)))
        .to eq(accounts_total: 0.0, investments_cost: 0.0, net_worth: 0.0)
    end

    # O ponto do ARCH-003: #call e .compute têm que concordar sempre, porque a
    # razão da extração é que as duas fórmulas duplicadas podiam divergir — e
    # divergiram, no FIN-002.
    it "agrees with the persisted snapshot produced by .call" do
      user = create(:user)
      create(:account, user: user, balance: 1234.56)
      create(:investment, user: user, ticker: "PETR4", quantity: 7, average_price: 33.33)
      create(:investment, :sell, user: user, ticker: "PETR4", quantity: 3, average_price: 40.10)

      totals = described_class.compute(user)
      snapshot = described_class.call(user)

      expect(snapshot.accounts_total.to_f).to eq(totals[:accounts_total])
      expect(snapshot.investments_cost.to_f).to eq(totals[:investments_cost])
      expect(snapshot.net_worth.to_f).to eq(totals[:net_worth])
    end
  end

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
