require "rails_helper"

RSpec.describe "Accounts API", type: :request do
  let(:user) { create(:user) }
  let(:headers) { auth_headers_for(user) }

  describe "GET /api/v1/accounts" do
    let!(:accounts) { create_list(:account, 3, user: user) }
    let!(:inactive)  { create(:account, :inactive, user: user) }

    it "returns only active accounts for current user" do
      get "/api/v1/accounts", headers: headers

      expect(response).to have_http_status(:ok)
      expect(json_response.length).to eq(3)
    end

    it "returns 401 without token" do
      get "/api/v1/accounts"
      expect(response).to have_http_status(:unauthorized)
    end
  end

  describe "GET /api/v1/accounts/:id" do
    let(:account) { create(:account, user: user) }

    it "returns the account" do
      get "/api/v1/accounts/#{account.id}", headers: headers

      expect(response).to have_http_status(:ok)
      expect(json_response[:id]).to eq(account.id)
    end

    it "returns 404 for another user's account" do
      other_account = create(:account, user: create(:user))
      get "/api/v1/accounts/#{other_account.id}", headers: headers

      expect(response).to have_http_status(:not_found)
    end
  end

  describe "POST /api/v1/accounts" do
    let(:valid_params) do
      { name: "Conta Nubank", institution: "Nubank", account_type: "checking", currency: "BRL" }
    end

    it "creates an account" do
      post "/api/v1/accounts", params: valid_params.to_json, headers: headers

      expect(response).to have_http_status(:created)
      expect(json_response[:name]).to eq("Conta Nubank")
    end

    it "returns errors for invalid params" do
      post "/api/v1/accounts", params: { name: "" }.to_json, headers: headers

      expect(response).to have_http_status(:unprocessable_content)
      expect(json_response[:errors]).to be_present
    end
  end

  describe "PATCH /api/v1/accounts/:id" do
    let(:account) { create(:account, user: user, name: "Old Name") }

    it "updates the account" do
      patch "/api/v1/accounts/#{account.id}",
        params: { name: "New Name" }.to_json, headers: headers

      expect(response).to have_http_status(:ok)
      expect(json_response[:name]).to eq("New Name")
    end
  end

  describe "DELETE /api/v1/accounts/:id" do
    let(:account) { create(:account, user: user) }

    it "soft-deletes the account" do
      delete "/api/v1/accounts/#{account.id}", headers: headers

      expect(response).to have_http_status(:no_content)
      expect(account.reload.active).to be(false)
    end
  end
end
