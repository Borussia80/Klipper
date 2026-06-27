require "rails_helper"

RSpec.describe "Budgets API", type: :request do
  let(:user)     { create(:user) }
  let(:headers)  { auth_headers_for(user) }
  let(:category) { create(:category, user: user, icon: "food") }
  let(:account)  { create(:account, user: user) }

  describe "GET /api/v1/budgets" do
    let!(:budget) { create(:budget, user: user, category: category) }

    it "returns budgets for current user" do
      get "/api/v1/budgets", headers: headers
      expect(response).to have_http_status(:ok)
      expect(json_response.length).to eq(1)
    end

    it "filters by year and month" do
      create(:budget, user: user, category: create(:category, user: user, icon: "x"),
        period_year: 2025, period_month: 1)
      get "/api/v1/budgets?year=#{budget.period_year}&month=#{budget.period_month}", headers: headers
      expect(json_response.length).to eq(1)
    end

    it "returns 401 without token" do
      get "/api/v1/budgets"
      expect(response).to have_http_status(:unauthorized)
    end
  end

  describe "GET /api/v1/budgets/summary" do
    let!(:budget) do
      create(:budget, user: user, category: category,
        amount_limit: 500, period_year: 2026, period_month: 6)
    end

    before do
      create(:transaction, user: user, account: account, category: category,
        amount: 200, transaction_type: "debit", occurred_on: Date.new(2026, 6, 10))
    end

    it "returns budget summary with spent amounts" do
      get "/api/v1/budgets/summary?year=2026&month=6", headers: headers
      expect(response).to have_http_status(:ok)
      row = json_response.first
      expect(row[:spent].to_f).to eq(200.0)
      expect(row[:remaining].to_f).to eq(300.0)
      expect(row[:pct_used].to_f).to eq(40.0)
    end
  end

  describe "POST /api/v1/budgets" do
    let(:valid_params) do
      { category_id: category.id, amount_limit: 800, period_month: 6, period_year: 2026 }
    end

    it "creates a budget" do
      post "/api/v1/budgets", params: valid_params.to_json, headers: headers
      expect(response).to have_http_status(:created)
      expect(json_response[:amount_limit].to_f).to eq(800.0)
    end

    it "rejects duplicate budget for same period" do
      create(:budget, user: user, category: category, period_year: 2026, period_month: 6)
      post "/api/v1/budgets", params: valid_params.to_json, headers: headers
      expect(response).to have_http_status(:unprocessable_content)
    end

    it "returns errors for invalid amount" do
      post "/api/v1/budgets",
        params: { category_id: category.id, amount_limit: -1, period_month: 6, period_year: 2026 }.to_json,
        headers: headers
      expect(response).to have_http_status(:unprocessable_content)
    end
  end

  describe "PATCH /api/v1/budgets/:id" do
    let(:budget) { create(:budget, user: user, category: category, amount_limit: 500) }

    it "updates the budget limit" do
      patch "/api/v1/budgets/#{budget.id}",
        params: { amount_limit: 750 }.to_json, headers: headers
      expect(response).to have_http_status(:ok)
      expect(json_response[:amount_limit].to_f).to eq(750.0)
    end
  end

  describe "DELETE /api/v1/budgets/:id" do
    let(:budget) { create(:budget, user: user, category: category) }

    it "destroys the budget" do
      delete "/api/v1/budgets/#{budget.id}", headers: headers
      expect(response).to have_http_status(:no_content)
      expect { budget.reload }.to raise_error(ActiveRecord::RecordNotFound)
    end
  end
end
