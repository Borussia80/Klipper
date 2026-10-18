require "rails_helper"

# D1 (docs/domain-research/03-specs/03-lancamentos.md, L-3 a L-6): o mesmo mês
# passa por todos os calculators que somam receita ou despesa. Transferência e
# pagamento de fatura movem dinheiro entre contas próprias e não podem virar
# renda nem gasto; o estorno devolve parte de uma compra e abate a despesa.
RSpec.describe "Semântica de receita e despesa nos calculators", type: :service do
  let(:user)     { create(:user) }
  let(:corrente) { create(:account, user: user) }
  let(:cartao)   { create(:account, user: user, account_type: "credit_card") }
  let(:renda)    { create(:category, :income, user: user, name: "Renda") }
  let(:mercado)  { create(:category, user: user, name: "Mercado", natureza: "variavel") }
  let(:lazer)    { create(:category, user: user, name: "Lazer", natureza: "variavel") }
  let(:dia)      { Date.new(2026, 6, 10) }

  def lanc(account, attrs)
    create(:transaction, user: user, account: account, occurred_on: dia, category: nil, **attrs)
  end

  before do
    lanc(corrente, description: "Salário", amount: 5000, transaction_type: "credit", category: renda)
    lanc(corrente, description: "Mercado", amount: 350, transaction_type: "debit", category: mercado)
    lanc(cartao, description: "Show", amount: 1200, transaction_type: "debit", category: lazer)
    lanc(cartao, description: "Estorno show", amount: 50, transaction_type: "credit", kind: "refund", category: lazer)
    lanc(corrente, description: "PAG BOLETO NU PAGAMENTOS SA", amount: 1200, transaction_type: "debit",
      kind: "card_payment")
    lanc(cartao, description: "Pagamento em 10 JUN", amount: 1200, transaction_type: "credit", kind: "card_payment")
    lanc(corrente, description: "Para a poupança", amount: 800, transaction_type: "transfer", category: nil)
    lanc(corrente, description: "Aluguel previsto", amount: 2500, transaction_type: "debit", category: mercado,
      status: "previsto")
  end

  it "MonthlySummaryCalculator: renda só do salário, despesa líquida do estorno" do
    result = MonthlySummaryCalculator.new(user, year: 2026, month: 6).call

    expect(result[:total_credits]).to eq(5000.0)
    expect(result[:total_debits]).to eq(1500.0)
    expect(result[:net]).to eq(3500.0)
    expect(result[:by_category].to_h { |r| [ r[:category_name], r[:total] ] })
      .to eq("Lazer" => 1150.0, "Mercado" => 350.0)
  end

  it "MonthlySeriesCalculator: o ponto do mês tem os mesmos totais" do
    point = MonthlySeriesCalculator.new(user, year: 2026, month: 6, months: 1).call[:points].last

    expect(point).to include(total_credits: 5000.0, total_debits: 1500.0, net: 3500.0)
  end

  it "NaturezaSplitCalculator: o total por natureza não inclui pagamento nem transferência" do
    result = NaturezaSplitCalculator.new(user, year: 2026, month: 6).call

    expect(result[:total]).to eq(1500.0)
    expect(result[:by_natureza].find { |r| r[:natureza] == "variavel" }[:total]).to eq(1500.0)
  end

  it "BudgetEngine: o estorno abate o gasto da categoria e o previsto não entra" do
    create(:budget, user: user, category: lazer, amount_limit: 2000, period_year: 2026, period_month: 6)
    create(:budget, user: user, category: mercado, amount_limit: 400, period_year: 2026, period_month: 6)
    rows = BudgetEngine.new(user, 2026, 6).summary.to_h { |r| [ r[:category_name], r[:spent] ] }

    expect(rows).to eq("Lazer" => 1150.0, "Mercado" => 350.0)
  end

  it "CategoryRecurrenceCalculator: categoria só com pagamento de fatura não conta como presente" do
    outra = create(:category, user: user, name: "Cartões")
    lanc(corrente, description: "FATURA PAGA PERSONNALITE", amount: 900, transaction_type: "debit",
      kind: "card_payment", category: outra)

    result = CategoryRecurrenceCalculator.new(user, outra, months: 1, reference_date: dia).call

    expect(result[:months_present]).to eq(0)
  end

  it "ReimbursementCoverageCalculator: gasto da categoria reembolsável desconta estorno e ignora transferência" do
    reembolso = create(:category, :income, user: user, name: "Reembolso plano")
    saude = create(:category, user: user, name: "Saúde", reimbursed_by_category: reembolso)
    lanc(corrente, description: "Consulta", amount: 400, transaction_type: "debit", category: saude)
    lanc(corrente, description: "Estorno consulta", amount: 100, transaction_type: "credit", kind: "refund",
      category: saude)
    lanc(corrente, description: "Para conta saúde", amount: 300, transaction_type: "transfer", category: saude)
    lanc(corrente, description: "Plano", amount: 150, transaction_type: "credit", category: reembolso)

    result = ReimbursementCoverageCalculator.new(user, saude, reference_date: dia).call

    expect(result[:spent]).to eq(300.0)
    expect(result[:reimbursed]).to eq(150.0)
    expect(result[:coverage_pct]).to eq(50.0)
  end
end
