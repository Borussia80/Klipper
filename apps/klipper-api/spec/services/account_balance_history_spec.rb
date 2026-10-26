require "rails_helper"

RSpec.describe AccountBalanceHistory do
  let(:user) { create(:user) }
  let(:account) { create(:account, user: user, opening_balance: 100, opening_balance_on: Date.new(2026, 10, 1)) }

  it "uses only effective entries and returns a running balance" do
    create(:transaction, user: user, account: account, amount: 20, transaction_type: "debit", occurred_on: Date.new(2026, 10, 2))
    create(:transaction, user: user, account: account, amount: 50, transaction_type: "credit", occurred_on: Date.new(2026, 10, 3))
    create(:transaction, user: user, account: account, amount: 999, status: "previsto", occurred_on: Date.new(2026, 10, 4))

    result = described_class.new(account, from: Date.new(2026, 10, 1), to: Date.new(2026, 10, 4)).call

    expect(result[:opening_balance]).to eq(100)
    expect(result[:closing_balance]).to eq(130)
    expect(result[:entries].map { |entry| entry[:balance] }).to eq([80, 130])
  end
end
