require 'rails_helper'

RSpec.describe "Api::V1::Reports", type: :request do
  let(:user) { create(:user) }
  let(:token) { JwtService.encode(user_id: user.id, token_version: user.token_version) }
  let(:auth_headers) { { "Authorization" => "Bearer #{token}" } }

  describe "GET /api/v1/reports/monthly" do
    let(:cat) { create(:category, user: user, name: "Alimentação", icon: "alimentacao") }

    before do
      create(:transaction, user: user, amount: 150.00, transaction_type: "debit",
             occurred_on: "2026-06-10", category: cat)
      create(:transaction, user: user, amount: 120.50, transaction_type: "debit",
             occurred_on: "2026-06-15", category: nil)
      create(:transaction, user: user, amount: 5000.00, transaction_type: "credit",
             occurred_on: "2026-06-05", category: nil)
      # different month — should NOT appear
      create(:transaction, user: user, amount: 999.00, transaction_type: "debit",
             occurred_on: "2026-05-20", category: cat)
    end

    it "returns 401 without token" do
      get "/api/v1/reports/monthly?year=2026&month=6"
      expect(response).to have_http_status(:unauthorized)
    end

    it "returns monthly summary with correct totals" do
      get "/api/v1/reports/monthly?year=2026&month=6", headers: auth_headers
      expect(response).to have_http_status(:ok)
      json = JSON.parse(response.body)
      expect(json["year"]).to eq(2026)
      expect(json["month"]).to eq(6)
      expect(json["total_debits"].to_f).to be_within(0.01).of(270.50)
      expect(json["total_credits"].to_f).to be_within(0.01).of(5000.00)
      expect(json["net"].to_f).to be_within(0.01).of(4729.50)
    end

    it "groups spending by category" do
      get "/api/v1/reports/monthly?year=2026&month=6", headers: auth_headers
      json = JSON.parse(response.body)
      cats = json["by_category"]
      expect(cats).to be_an(Array)
      alimentacao = cats.find { |c| c["category_name"] == "Alimentação" }
      expect(alimentacao).not_to be_nil
      expect(alimentacao["total"].to_f).to be_within(0.01).of(150.00)
    end

    it "includes uncategorized transactions" do
      get "/api/v1/reports/monthly?year=2026&month=6", headers: auth_headers
      json = JSON.parse(response.body)
      sem_cat = json["by_category"].find { |c| c["category_name"] == "Sem categoria" }
      expect(sem_cat).not_to be_nil
      expect(sem_cat["total"].to_f).to be_within(0.01).of(120.50)
    end

    it "defaults to current month when params omitted" do
      get "/api/v1/reports/monthly", headers: auth_headers
      expect(response).to have_http_status(:ok)
    end

    it "does not include other users' transactions" do
      other = create(:user)
      create(:transaction, user: other, amount: 9999.00, transaction_type: "debit", occurred_on: "2026-06-01")
      get "/api/v1/reports/monthly?year=2026&month=6", headers: auth_headers
      json = JSON.parse(response.body)
      expect(json["total_debits"].to_f).to be_within(0.01).of(270.50)
    end

    it "filters by member_id" do
      member = create(:member, user: user)
      create(:transaction, user: user, amount: 300.00, transaction_type: "debit",
             occurred_on: "2026-06-12", category: cat, member: member)

      get "/api/v1/reports/monthly?year=2026&month=6&member_id=#{member.id}", headers: auth_headers
      json = JSON.parse(response.body)
      expect(json["total_debits"].to_f).to be_within(0.01).of(300.00)
    end
  end

  describe "GET /api/v1/reports/natureza_split" do
    let(:fixo)               { create(:category, :fixo, user: user, name: "Aluguel") }
    let(:cartao_parcelamento) { create(:category, :cartao_parcelamento, user: user, name: "Cartão") }
    let(:variavel)           { create(:category, :variavel, user: user, name: "Lazer") }

    before do
      create(:transaction, user: user, amount: 600.00, transaction_type: "debit",
             occurred_on: "2026-06-05", category: fixo)
      create(:transaction, user: user, amount: 300.00, transaction_type: "debit",
             occurred_on: "2026-06-10", category: cartao_parcelamento)
      create(:transaction, user: user, amount: 100.00, transaction_type: "debit",
             occurred_on: "2026-06-15", category: variavel)
      # credit — should not count
      create(:transaction, user: user, amount: 5000.00, transaction_type: "credit",
             occurred_on: "2026-06-05", category: fixo)
      # uncategorized — should be excluded from the total
      create(:transaction, user: user, amount: 50.00, transaction_type: "debit",
             occurred_on: "2026-06-20", category: nil)
      # different month — should NOT appear
      create(:transaction, user: user, amount: 999.00, transaction_type: "debit",
             occurred_on: "2026-05-20", category: fixo)
    end

    it "returns 401 without token" do
      get "/api/v1/reports/natureza_split?year=2026&month=6"
      expect(response).to have_http_status(:unauthorized)
    end

    it "groups debit totals by category natureza" do
      get "/api/v1/reports/natureza_split?year=2026&month=6", headers: auth_headers
      expect(response).to have_http_status(:ok)
      json = JSON.parse(response.body)

      expect(json["year"]).to eq(2026)
      expect(json["month"]).to eq(6)
      expect(json["total"].to_f).to be_within(0.01).of(1000.00)

      by_natureza = json["by_natureza"].index_by { |r| r["natureza"] }
      expect(by_natureza["fixo"]["total"].to_f).to be_within(0.01).of(600.00)
      expect(by_natureza["cartao_parcelamento"]["total"].to_f).to be_within(0.01).of(300.00)
      expect(by_natureza["variavel"]["total"].to_f).to be_within(0.01).of(100.00)
    end

    it "percentages sum to approximately 100" do
      get "/api/v1/reports/natureza_split?year=2026&month=6", headers: auth_headers
      json = JSON.parse(response.body)
      total_pct = json["by_natureza"].sum { |r| r["pct"].to_f }
      expect(total_pct).to be_within(0.2).of(100.0)
    end

    it "excludes credits and other months" do
      get "/api/v1/reports/natureza_split?year=2026&month=6", headers: auth_headers
      json = JSON.parse(response.body)
      by_natureza = json["by_natureza"].index_by { |r| r["natureza"] }
      expect(by_natureza["fixo"]["total"].to_f).to be_within(0.01).of(600.00)
    end

    it "excludes uncategorized transactions from the total" do
      get "/api/v1/reports/natureza_split?year=2026&month=6", headers: auth_headers
      json = JSON.parse(response.body)
      expect(json["total"].to_f).to be_within(0.01).of(1000.00)
    end

    it "filters by member_id" do
      member = create(:member, user: user)
      create(:transaction, user: user, amount: 200.00, transaction_type: "debit",
             occurred_on: "2026-06-12", category: fixo, member: member)

      get "/api/v1/reports/natureza_split?year=2026&month=6&member_id=#{member.id}", headers: auth_headers
      json = JSON.parse(response.body)
      expect(json["total"].to_f).to be_within(0.01).of(200.00)
    end

    it "does not include other users' transactions" do
      other = create(:user)
      other_cat = create(:category, :fixo, user: other)
      create(:transaction, user: other, amount: 9999.00, transaction_type: "debit",
             occurred_on: "2026-06-01", category: other_cat)

      get "/api/v1/reports/natureza_split?year=2026&month=6", headers: auth_headers
      json = JSON.parse(response.body)
      expect(json["total"].to_f).to be_within(0.01).of(1000.00)
    end
  end

  describe "GET /api/v1/reports/reimbursement_coverage" do
    let(:income)  { create(:category, :income, user: user, name: "Reembolso Bradesco") }
    let(:expense) { create(:category, user: user, name: "Terapia Pedro", reimbursed_by_category: income) }
    let(:unlinked) { create(:category, user: user, name: "Mercado") }

    def debit_in(cat:, amount:, on:)
      create(:transaction, user: user, category: cat, amount: amount,
             transaction_type: "debit", occurred_on: on)
    end

    def credit_in(cat:, amount:, on:)
      create(:transaction, user: user, category: cat, amount: amount,
             transaction_type: "credit", occurred_on: on)
    end

    it "returns 401 without token" do
      get "/api/v1/reports/reimbursement_coverage?year=2026&month=7"
      expect(response).to have_http_status(:unauthorized)
    end

    it "only returns expense categories with a reimbursement link" do
      debit_in(cat: expense, amount: 400, on: "2026-07-05")
      debit_in(cat: unlinked, amount: 200, on: "2026-07-05")

      get "/api/v1/reports/reimbursement_coverage?year=2026&month=7", headers: auth_headers
      json = JSON.parse(response.body)
      names = json["categories"].map { |c| c["category_name"] }
      expect(names).to include("Terapia Pedro")
      expect(names).not_to include("Mercado")
    end

    it "filters by category_id" do
      other_income = create(:category, :income, user: user, name: "Outro reembolso")
      other_expense = create(:category, user: user, name: "Fisio", reimbursed_by_category: other_income)
      debit_in(cat: expense, amount: 400, on: "2026-07-05")
      debit_in(cat: other_expense, amount: 200, on: "2026-07-05")

      get "/api/v1/reports/reimbursement_coverage?year=2026&month=7&category_id=#{expense.id}", headers: auth_headers
      json = JSON.parse(response.body)
      expect(json["categories"].length).to eq(1)
      expect(json["categories"].first["category_name"]).to eq("Terapia Pedro")
    end

    it "does not include other users' categories" do
      other = create(:user)
      other_income = create(:category, :income, user: other)
      create(:category, user: other, reimbursed_by_category: other_income, name: "Categoria de outro usuário")

      get "/api/v1/reports/reimbursement_coverage?year=2026&month=7", headers: auth_headers
      json = JSON.parse(response.body)
      names = json["categories"].map { |c| c["category_name"] }
      expect(names).not_to include("Categoria de outro usuário")
    end

    it "returns correct payload with 6 months of history and a drop in the current month" do
      (1..6).each do |i|
        d = Date.new(2026, 7, 1).prev_month(i)
        debit_in(cat: expense, amount: 100, on: d.strftime("%Y-%m-05"))
        credit_in(cat: income, amount: 80, on: d.strftime("%Y-%m-05"))
      end
      debit_in(cat: expense, amount: 100, on: "2026-07-05")
      credit_in(cat: income, amount: 30, on: "2026-07-05")

      get "/api/v1/reports/reimbursement_coverage?year=2026&month=7", headers: auth_headers
      json = JSON.parse(response.body)
      row = json["categories"].find { |c| c["category_name"] == "Terapia Pedro" }

      expect(row["reimbursed_by_category_name"]).to eq("Reembolso Bradesco")
      expect(row["spent"].to_f).to be_within(0.01).of(100.0)
      expect(row["reimbursed"].to_f).to be_within(0.01).of(30.0)
      expect(row["coverage_pct"].to_f).to be_within(0.1).of(30.0)
      expect(row["historical_avg_pct"].to_f).to be_within(0.1).of(80.0)
      expect(row["alert"]).to be true
    end
  end

  describe "GET /api/v1/reports/debt_ranking" do
    it "returns 401 without token" do
      get "/api/v1/reports/debt_ranking"
      expect(response).to have_http_status(:unauthorized)
    end

    it "returns cards ranked by cost and matches the real Itaú invoice figures" do
      create(:account, :with_debt_data, user: user)

      get "/api/v1/reports/debt_ranking", headers: auth_headers
      json = JSON.parse(response.body)
      row = json["cards"].first

      expect(row["saldo_fatura_atual"].to_f).to eq(9603.90)
      expect(row["saldo_projetado_proximo_mes"].to_f).to be_within(1.0).of(10_780.76)
    end

    it "does not include other users' cards" do
      other = create(:user)
      create(:account, :with_debt_data, user: other, name: "Cartão de outro usuário")

      get "/api/v1/reports/debt_ranking", headers: auth_headers
      json = JSON.parse(response.body)
      expect(json["cards"]).to be_empty
    end
  end

  describe "GET /api/v1/reports/net_worth" do
    before do
      create(:account, user: user, balance: 3000.00)
      create(:account, user: user, balance: 1500.50)
      create(:investment, user: user, quantity: 100, average_price: 150.00)  # cost = 15000
      create(:investment, :fii, user: user, quantity: 50, average_price: 200.00)  # cost = 10000
    end

    it "returns 401 without token" do
      get "/api/v1/reports/net_worth"
      expect(response).to have_http_status(:unauthorized)
    end

    it "returns net worth combining accounts + investments" do
      get "/api/v1/reports/net_worth", headers: auth_headers
      expect(response).to have_http_status(:ok)
      json = JSON.parse(response.body)
      expect(json["accounts_total"].to_f).to be_within(0.01).of(4500.50)
      expect(json["investments_cost"].to_f).to be_within(0.01).of(25000.00)
      expect(json["net_worth"].to_f).to be_within(0.01).of(29500.50)
    end

    it "includes accounts list" do
      get "/api/v1/reports/net_worth", headers: auth_headers
      json = JSON.parse(response.body)
      expect(json["accounts"]).to be_an(Array)
      expect(json["accounts"].length).to eq(2)
    end

    it "includes investments grouped by type" do
      get "/api/v1/reports/net_worth", headers: auth_headers
      json = JSON.parse(response.body)
      expect(json["investments_by_type"]).to be_an(Array)
    end

    it "creates a snapshot for the current month on first call" do
      expect {
        get "/api/v1/reports/net_worth", headers: auth_headers
      }.to change { NetWorthSnapshot.where(user: user).count }.from(0).to(1)

      snapshot = NetWorthSnapshot.find_by(user: user, year: Date.current.year, month: Date.current.month)
      expect(snapshot.net_worth.to_f).to be_within(0.01).of(29500.50)
    end

    it "updates the existing snapshot instead of duplicating it when called again in the same month" do
      get "/api/v1/reports/net_worth", headers: auth_headers
      create(:account, user: user, balance: 999.50)

      expect {
        get "/api/v1/reports/net_worth", headers: auth_headers
      }.not_to change { NetWorthSnapshot.where(user: user).count }

      snapshot = NetWorthSnapshot.find_by(user: user, year: Date.current.year, month: Date.current.month)
      expect(snapshot.net_worth.to_f).to be_within(0.01).of(30500.00)
    end
  end

  describe "GET /api/v1/reports/net_worth_history" do
    it "returns 401 without token" do
      get "/api/v1/reports/net_worth_history"
      expect(response).to have_http_status(:unauthorized)
    end

    it "returns snapshots ordered chronologically" do
      create(:net_worth_snapshot, user: user, year: 2026, month: 5, net_worth: 1000)
      create(:net_worth_snapshot, user: user, year: 2026, month: 3, net_worth: 800)
      create(:net_worth_snapshot, user: user, year: 2026, month: 4, net_worth: 900)

      get "/api/v1/reports/net_worth_history", headers: auth_headers
      expect(response).to have_http_status(:ok)
      json = JSON.parse(response.body)
      expect(json["points"].map { |p| p["month"] }).to eq([ 3, 4, 5 ])
      expect(json["points"].last["net_worth"].to_f).to be_within(0.01).of(1000.0)
    end

    it "filters to the last N months when a period is given" do
      base = Date.current.beginning_of_month
      (0..5).each do |i|
        d = base.prev_month(i)
        create(:net_worth_snapshot, user: user, year: d.year, month: d.month, net_worth: 100 * i)
      end

      get "/api/v1/reports/net_worth_history?period=3m", headers: auth_headers
      json = JSON.parse(response.body)
      expect(json["points"].length).to eq(3)
    end

    it "does not include other users' snapshots" do
      other = create(:user)
      create(:net_worth_snapshot, user: other)

      get "/api/v1/reports/net_worth_history", headers: auth_headers
      json = JSON.parse(response.body)
      expect(json["points"]).to be_empty
    end
  end
end
