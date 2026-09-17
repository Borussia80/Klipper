require "rails_helper"

RSpec.describe ReimbursementCoverageCalculator, type: :service do
  let(:user)    { create(:user) }
  let(:account) { create(:account, user: user) }
  let(:income)  { create(:category, :income, user: user, name: "Reembolso Convênio") }
  let(:expense) do
    create(:category, user: user, name: "Terapia", reimbursed_by_category: income)
  end
  let(:reference_date) { Date.new(2026, 7, 15) }

  def debit_in(year:, month:, amount:, cat: expense)
    create(:transaction, user: user, account: account, category: cat,
      transaction_type: "debit", amount: amount, occurred_on: Date.new(year, month, 5))
  end

  def credit_in(year:, month:, amount:, cat: income)
    create(:transaction, user: user, account: account, category: cat,
      transaction_type: "credit", amount: amount, occurred_on: Date.new(year, month, 5))
  end

  subject(:result) do
    described_class.new(user, expense, months: months, reference_date: reference_date).call
  end

  let(:months) { ReimbursementCoverageCalculator::DEFAULT_MONTHS }

  it "returns nil when the category has no reimbursement link" do
    unlinked = create(:category, user: user, name: "Sem vínculo")
    result = described_class.new(user, unlinked, reference_date: reference_date).call
    expect(result).to be_nil
  end

  it "calculates coverage_pct as reimbursed/spent for the current month" do
    debit_in(year: 2026, month: 7, amount: 400)
    credit_in(year: 2026, month: 7, amount: 300)

    expect(result[:spent]).to eq(400.0)
    expect(result[:reimbursed]).to eq(300.0)
    expect(result[:coverage_pct]).to eq(75.0)
  end

  it "returns nil coverage_pct without raising when there is no spending in the current month" do
    expect { result }.not_to raise_error
    expect(result[:spent]).to eq(0.0)
    expect(result[:coverage_pct]).to be_nil
  end

  it "returns nil historical_avg_pct when there is no history" do
    debit_in(year: 2026, month: 7, amount: 400)
    credit_in(year: 2026, month: 7, amount: 300)

    expect(result[:historical_avg_pct]).to be_nil
    expect(result[:months_considered]).to eq(0)
  end

  it "ignores historical months with no spending when averaging" do
    debit_in(year: 2026, month: 6, amount: 200)
    credit_in(year: 2026, month: 6, amount: 200) # 100%
    # month 2026-05 has no spending at all — should not count toward months_considered
    debit_in(year: 2026, month: 7, amount: 100)
    credit_in(year: 2026, month: 7, amount: 100)

    expect(result[:months_considered]).to eq(1)
    expect(result[:historical_avg_pct]).to eq(100.0)
  end

  it "flags alert: true when coverage stays below half of the historical average" do
    # 2026-01..04 at 80% coverage
    (3..6).each do |i|
      d = reference_date.prev_month(i)
      debit_in(year: d.year, month: d.month, amount: 100)
      credit_in(year: d.year, month: d.month, amount: 80)
    end
    # then three months in a row at 30% — a drop that holds, not a late payment
    (1..2).each do |i|
      d = reference_date.prev_month(i)
      debit_in(year: d.year, month: d.month, amount: 100)
      credit_in(year: d.year, month: d.month, amount: 30)
    end
    debit_in(year: 2026, month: 7, amount: 100)
    credit_in(year: 2026, month: 7, amount: 30)

    expect(result[:historical_avg_pct]).to eq(63.3)
    expect(result[:coverage_pct]).to eq(30.0)
    expect(result[:alert]).to be true
  end

  it "flags alert: false when a single month's reimbursement is merely late" do
    # 6 historical months at 80% coverage
    (1..6).each do |i|
      d = reference_date.prev_month(i)
      debit_in(year: d.year, month: d.month, amount: 100)
      credit_in(year: d.year, month: d.month, amount: 80)
    end
    # the convênio hasn't paid July yet: the month reads 0%, but nothing is wrong
    debit_in(year: 2026, month: 7, amount: 100)

    expect(result[:coverage_pct]).to eq(0.0)
    expect(result[:alert]).to be false
  end

  it "flags alert: false when the drop is small" do
    (1..6).each do |i|
      d = reference_date.prev_month(i)
      debit_in(year: d.year, month: d.month, amount: 100)
      credit_in(year: d.year, month: d.month, amount: 80)
    end
    debit_in(year: 2026, month: 7, amount: 100)
    credit_in(year: 2026, month: 7, amount: 60)

    expect(result[:alert]).to be false
  end

  it "flags alert: false when there is no spending in the current month" do
    (1..6).each do |i|
      d = reference_date.prev_month(i)
      debit_in(year: d.year, month: d.month, amount: 100)
      credit_in(year: d.year, month: d.month, amount: 80)
    end

    expect(result[:coverage_pct]).to be_nil
    expect(result[:alert]).to be false
  end

  it "flags alert: false when there is no historical data" do
    debit_in(year: 2026, month: 7, amount: 100)
    credit_in(year: 2026, month: 7, amount: 10)

    expect(result[:historical_avg_pct]).to be_nil
    expect(result[:alert]).to be false
  end

  # FIN-009: reembolso é lançado no mês em que o dinheiro cai, não no mês do gasto
  # que ele cobre. Então cobertura acima de 100% é o caso normal de um reembolso
  # atrasado entrando agora, e é informação que o usuário quer ver — este teste
  # existe para que ninguém "conserte" isso com um teto em 100 por achar que é bug.
  # A barra na tela tem overflow: hidden, então o excesso é recortado sem quebrar
  # o layout.
  it "reports coverage above 100% instead of capping it, when a late reimbursement lands" do
    debit_in(year: 2026, month: 7, amount: 100)
    credit_in(year: 2026, month: 7, amount: 250)

    expect(result[:spent]).to eq(100.0)
    expect(result[:reimbursed]).to eq(250.0)
    expect(result[:coverage_pct]).to eq(250.0)
  end

  it "reports coverage above 100% in the historical average too" do
    d = reference_date.prev_month(1)
    debit_in(year: d.year, month: d.month, amount: 100)
    credit_in(year: d.year, month: d.month, amount: 300)
    debit_in(year: 2026, month: 7, amount: 100)
    credit_in(year: 2026, month: 7, amount: 100)

    expect(result[:historical_avg_pct]).to eq(300.0)
  end

  it "respects a custom months: window" do
    d = reference_date.prev_month(1)
    debit_in(year: d.year, month: d.month, amount: 100)
    credit_in(year: d.year, month: d.month, amount: 50)

    d2 = reference_date.prev_month(2)
    debit_in(year: d2.year, month: d2.month, amount: 100)
    credit_in(year: d2.year, month: d2.month, amount: 90)

    result_1_month = described_class.new(user, expense, months: 1, reference_date: reference_date).call
    expect(result_1_month[:months_considered]).to eq(1)
    expect(result_1_month[:historical_avg_pct]).to eq(50.0)
  end
end
