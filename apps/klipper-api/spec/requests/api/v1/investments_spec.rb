require "rails_helper"

RSpec.describe "Investments API", type: :request do
  let(:user)    { create(:user) }
  let(:headers) { auth_headers_for(user) }

  describe "GET /api/v1/investments" do
    let!(:stock) { create(:investment, user: user, investment_type: "stock") }
    let!(:fii)   { create(:investment, :fii, user: user) }

    it "returns all investments for current user" do
      get "/api/v1/investments", headers: headers
      expect(response).to have_http_status(:ok)
      expect(json_response.length).to eq(2)
    end

    it "filters by type" do
      get "/api/v1/investments?type=fii", headers: headers
      expect(json_response.length).to eq(1)
      expect(json_response.first[:investment_type]).to eq("fii")
    end

    it "returns 401 without token" do
      get "/api/v1/investments"
      expect(response).to have_http_status(:unauthorized)
    end
  end

  describe "GET /api/v1/investments/portfolio" do
    before do
      create(:investment, user: user, investment_type: "stock",
        quantity: 10, average_price: 100)
      create(:investment, :fii, user: user,
        quantity: 5, average_price: 200)
    end

    it "returns portfolio totals" do
      get "/api/v1/investments/portfolio", headers: headers
      expect(response).to have_http_status(:ok)
      expect(json_response[:total_positions]).to eq(2)
      expect(json_response[:total_cost].to_f).to eq(2000.0)
      expect(json_response[:by_type]).to be_an(Array)
    end
  end

  describe "GET /api/v1/investments/:id" do
    let(:investment) { create(:investment, user: user) }

    it "returns the investment" do
      get "/api/v1/investments/#{investment.id}", headers: headers
      expect(response).to have_http_status(:ok)
      expect(json_response[:id]).to eq(investment.id)
    end

    it "returns 404 for another user's investment" do
      other = create(:investment, user: create(:user))
      get "/api/v1/investments/#{other.id}", headers: headers
      expect(response).to have_http_status(:not_found)
    end
  end

  describe "POST /api/v1/investments" do
    let(:valid_params) do
      {
        ticker: "PETR4",
        name: "Petrobras PN",
        investment_type: "stock",
        quantity: 100,
        average_price: 38.50,
        currency: "BRL"
      }
    end

    it "creates an investment" do
      post "/api/v1/investments", params: valid_params.to_json, headers: headers
      expect(response).to have_http_status(:created)
      expect(json_response[:ticker]).to eq("PETR4")
    end

    it "returns errors for invalid params" do
      post "/api/v1/investments",
        params: { name: "", investment_type: "stock", quantity: 0, average_price: 0, currency: "BRL" }.to_json,
        headers: headers
      expect(response).to have_http_status(:unprocessable_content)
    end
  end

  describe "POST /api/v1/investments — operation_type e occurred_on (P0.1/P0.2)" do
    let(:base_params) do
      {
        ticker: "IVVB11",
        name: "IVVB11",
        investment_type: "etf",
        currency: "BRL"
      }
    end

    it "persists operation_type and occurred_on from the payload" do
      post "/api/v1/investments",
        params: base_params.merge(quantity: 10, average_price: 100,
          operation_type: "buy", occurred_on: "2026-08-01").to_json,
        headers: headers
      expect(response).to have_http_status(:created)
      expect(json_response[:operation_type]).to eq("buy")
      expect(json_response[:occurred_on]).to eq("2026-08-01")
    end

    it "rejects a sell with no prior position, without persisting it" do
      expect {
        post "/api/v1/investments",
          params: base_params.merge(quantity: 10, average_price: 100, operation_type: "sell").to_json,
          headers: headers
      }.not_to change(Investment, :count)
      expect(response).to have_http_status(:unprocessable_content)
    end

    it "accepts a sell that does not exceed the held position" do
      post "/api/v1/investments",
        params: base_params.merge(quantity: 10, average_price: 100, operation_type: "buy").to_json,
        headers: headers
      expect(response).to have_http_status(:created)

      post "/api/v1/investments",
        params: base_params.merge(quantity: 4, average_price: 120, operation_type: "sell").to_json,
        headers: headers
      expect(response).to have_http_status(:created)

      get "/api/v1/investments/portfolio", headers: headers
      expect(json_response[:total_cost].to_f).to eq(520.0)
    end

    it "rejects an occurred_on in the future" do
      post "/api/v1/investments",
        params: base_params.merge(quantity: 10, average_price: 100,
          occurred_on: (Time.zone.today + 1).to_s).to_json,
        headers: headers
      expect(response).to have_http_status(:unprocessable_content)
    end
  end

  describe "PATCH /api/v1/investments/:id" do
    let(:investment) { create(:investment, user: user, quantity: 10) }

    it "updates the investment" do
      patch "/api/v1/investments/#{investment.id}",
        params: { quantity: 20 }.to_json, headers: headers
      expect(response).to have_http_status(:ok)
      expect(json_response[:quantity].to_f).to eq(20.0)
    end
  end

  describe "SEC-04: BOLA em account_id (cross-user)" do
    let(:other_user)    { create(:user) }
    let(:other_account) { create(:account, user: other_user) }

    it "rejects account_id de outro usuário na criação" do
      post "/api/v1/investments",
        params: { account_id: other_account.id, ticker: "PETR4", name: "Petrobras PN",
                   investment_type: "stock", quantity: 100, average_price: 38.50, currency: "BRL" }.to_json,
        headers: headers
      expect(response).to have_http_status(:unprocessable_content)
    end

    it "rejects account_id de outro usuário na atualização" do
      investment = create(:investment, user: user)
      patch "/api/v1/investments/#{investment.id}",
        params: { account_id: other_account.id }.to_json, headers: headers
      expect(response).to have_http_status(:unprocessable_content)
      expect(investment.reload.account_id).to be_nil
    end
  end

  describe "DELETE /api/v1/investments/:id" do
    let(:investment) { create(:investment, user: user) }

    it "destroys the investment" do
      delete "/api/v1/investments/#{investment.id}", headers: headers
      expect(response).to have_http_status(:no_content)
      expect { investment.reload }.to raise_error(ActiveRecord::RecordNotFound)
    end
  end
end
