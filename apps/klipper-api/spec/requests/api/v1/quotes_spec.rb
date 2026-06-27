require 'rails_helper'

RSpec.describe "Api::V1::Quotes", type: :request do
  let(:user) { create(:user) }
  let(:token) { JwtService.encode(user_id: user.id) }
  let(:auth_headers) { { "Authorization" => "Bearer #{token}" } }

  let(:brapi_response) do
    {
      results: [
        { symbol: "PETR4", regularMarketPrice: 38.50, regularMarketChangePercent: 1.23, longName: "Petroleo Brasileiro S.A." },
        { symbol: "VALE3", regularMarketPrice: 61.20, regularMarketChangePercent: -0.45, longName: "Vale S.A." },
      ]
    }.to_json
  end

  before do
    stub_request(:get, /brapi\.dev/)
      .to_return(status: 200, body: brapi_response, headers: { 'Content-Type' => 'application/json' })
  end

  describe "GET /api/v1/quotes" do
    it "returns 401 without token" do
      get "/api/v1/quotes?tickers=PETR4"
      expect(response).to have_http_status(:unauthorized)
    end

    it "returns quotes for requested tickers" do
      get "/api/v1/quotes?tickers=PETR4,VALE3", headers: auth_headers
      expect(response).to have_http_status(:ok)
      json = JSON.parse(response.body)
      expect(json["quotes"]).to be_an(Array)
      expect(json["quotes"].length).to eq(2)
    end

    it "returns ticker, price, change_pct and name" do
      get "/api/v1/quotes?tickers=PETR4,VALE3", headers: auth_headers
      json = JSON.parse(response.body)
      petr4 = json["quotes"].find { |q| q["ticker"] == "PETR4" }
      expect(petr4["price"]).to eq(38.50)
      expect(petr4["change_pct"]).to eq(1.23)
      expect(petr4["name"]).to eq("Petroleo Brasileiro S.A.")
    end

    it "returns cached_at timestamp" do
      get "/api/v1/quotes?tickers=PETR4", headers: auth_headers
      json = JSON.parse(response.body)
      expect(json["cached_at"]).not_to be_nil
    end

    it "returns 422 when tickers param is missing" do
      get "/api/v1/quotes", headers: auth_headers
      expect(response).to have_http_status(:unprocessable_entity)
    end

    it "calls brapi.dev only once when making two requests with same tickers (cache hit)" do
      Rails.cache.clear
      2.times { get "/api/v1/quotes?tickers=PETR4", headers: auth_headers }
      expect(a_request(:get, /brapi\.dev/)).to have_been_made.once
    end
  end
end
