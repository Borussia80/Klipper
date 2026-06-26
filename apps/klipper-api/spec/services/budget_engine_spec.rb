require "rails_helper"

RSpec.describe BudgetEngine, type: :service do
  let(:user)     { create(:user) }
  let(:account)  { create(:account, user: user) }
  let(:category) { create(:category, user: user, name: "Alimentação", icon: "food") }
  let!(:budget) do
    create(:budget, user: user, category: category,
      amount_limit: 1000, period_year: 2026, period_month: 6)
  end

  subject(:engine) { described_class.new(user, 2026, 6) }

  it "calculates spent, remaining, and pct_used correctly" do
    create(:transaction, user: user, account: account, category: category,
      amount: 300, transaction_type: "debit", occurred_on: Date.new(2026, 6, 15))

    result = engine.summary
    expect(result.length).to eq(1)

    row = result.first
    expect(row[:spent]).to eq(300)
    expect(row[:remaining]).to eq(700)
    expect(row[:pct_used]).to eq(30.0)
    expect(row[:category_name]).to eq("Alimentação")
  end

  it "sums multiple debit transactions in the month" do
    create(:transaction, user: user, account: account, category: category,
      amount: 200, transaction_type: "debit", occurred_on: Date.new(2026, 6, 1))
    create(:transaction, user: user, account: account, category: category,
      amount: 150, transaction_type: "debit", occurred_on: Date.new(2026, 6, 28))

    result = engine.summary
    expect(result.first[:spent]).to eq(350)
  end

  it "excludes credit transactions from spending" do
    create(:transaction, user: user, account: account, category: category,
      amount: 500, transaction_type: "credit", occurred_on: Date.new(2026, 6, 10))

    result = engine.summary
    expect(result.first[:spent]).to eq(0)
  end

  it "excludes transactions from other months" do
    create(:transaction, user: user, account: account, category: category,
      amount: 400, transaction_type: "debit", occurred_on: Date.new(2026, 5, 31))

    result = engine.summary
    expect(result.first[:spent]).to eq(0)
  end

  it "returns empty array when no budgets in period" do
    result = described_class.new(user, 2025, 1).summary
    expect(result).to be_empty
  end

  it "returns 0 pct_used when amount_limit is zero" do
    budget.update_column(:amount_limit, 0)
    result = engine.summary
    expect(result.first[:pct_used]).to eq(0.0)
  end
end
