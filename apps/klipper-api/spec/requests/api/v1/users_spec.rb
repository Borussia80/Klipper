require 'rails_helper'

RSpec.describe "Api::V1::Users", type: :request do
  let(:user) { create(:user, name: "Roberto Milet", email: "roberto@example.com", password: "secret123", password_confirmation: "secret123") }
  let(:token) { JwtService.encode(user_id: user.id) }
  let(:auth_headers) { { "Authorization" => "Bearer #{token}" } }

  describe "GET /api/v1/users/me" do
    it "returns 200 with current user data when authenticated" do
      get "/api/v1/users/me", headers: auth_headers
      expect(response).to have_http_status(:ok)
      json = JSON.parse(response.body)
      expect(json["id"]).to eq(user.id)
      expect(json["email"]).to eq("roberto@example.com")
      expect(json["name"]).to eq("Roberto Milet")
      expect(json.keys).not_to include("password_digest")
    end

    it "returns 401 without token" do
      get "/api/v1/users/me"
      expect(response).to have_http_status(:unauthorized)
    end
  end

  describe "PATCH /api/v1/users/me" do
    it "updates name and returns updated user" do
      patch "/api/v1/users/me",
        params: { name: "Roberto M. Atualizado" },
        headers: auth_headers
      expect(response).to have_http_status(:ok)
      json = JSON.parse(response.body)
      expect(json["name"]).to eq("Roberto M. Atualizado")
      expect(user.reload.name).to eq("Roberto M. Atualizado")
    end

    it "updates email" do
      patch "/api/v1/users/me",
        params: { email: "novo@example.com" },
        headers: auth_headers
      expect(response).to have_http_status(:ok)
      expect(user.reload.email).to eq("novo@example.com")
    end

    it "returns 422 with invalid email" do
      patch "/api/v1/users/me",
        params: { email: "not-an-email" },
        headers: auth_headers
      expect(response).to have_http_status(:unprocessable_content)
    end

    it "returns 401 without token" do
      patch "/api/v1/users/me", params: { name: "X" }
      expect(response).to have_http_status(:unauthorized)
    end
  end

  describe "POST /api/v1/users/password" do
    it "changes password when current_password is correct" do
      post "/api/v1/users/password",
        params: { current_password: "secret123", password: "newpass456", password_confirmation: "newpass456" },
        headers: auth_headers
      expect(response).to have_http_status(:ok)
      expect(user.reload.authenticate("newpass456")).to be_truthy
    end

    it "returns 422 when current_password is wrong" do
      post "/api/v1/users/password",
        params: { current_password: "wrongpass", password: "newpass456", password_confirmation: "newpass456" },
        headers: auth_headers
      expect(response).to have_http_status(:unprocessable_content)
      json = JSON.parse(response.body)
      expect(json["error"]).to match(/senha atual/i)
    end

    it "returns 422 when password_confirmation doesn't match" do
      post "/api/v1/users/password",
        params: { current_password: "secret123", password: "newpass456", password_confirmation: "different" },
        headers: auth_headers
      expect(response).to have_http_status(:unprocessable_content)
    end

    it "returns 401 without token" do
      post "/api/v1/users/password", params: { current_password: "x", password: "y", password_confirmation: "y" }
      expect(response).to have_http_status(:unauthorized)
    end
  end
end
