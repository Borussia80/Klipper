require 'rails_helper'

RSpec.describe "Api::V1::Reports", type: :request do
  let(:user) { create(:user) }
  let(:token) { JwtService.encode(user_id: user.id) }
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
  end
end
