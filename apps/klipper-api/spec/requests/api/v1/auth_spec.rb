require "rails_helper"

RSpec.describe "Auth endpoints", type: :request do
  describe "POST /api/v1/auth/sign_up" do
    let(:valid_params) do
      { email: "new@example.com", password: "password123", password_confirmation: "password123", name: "Test User" }
    end

    context "with valid params" do
      it "creates a user and returns a token" do
        post "/api/v1/auth/sign_up", params: valid_params.to_json,
          headers: { "Content-Type" => "application/json" }

        expect(response).to have_http_status(:created)
        expect(json_response[:token]).to be_present
        expect(json_response[:user][:email]).to eq("new@example.com")
      end
    end

    context "with duplicate email" do
      before { create(:user, email: "new@example.com") }

      it "returns unprocessable_entity" do
        post "/api/v1/auth/sign_up", params: valid_params.to_json,
          headers: { "Content-Type" => "application/json" }

        expect(response).to have_http_status(:unprocessable_content)
        expect(json_response[:errors]).to be_present
      end
    end

    context "with missing password" do
      it "returns unprocessable_entity" do
        post "/api/v1/auth/sign_up",
          params: { email: "new@example.com" }.to_json,
          headers: { "Content-Type" => "application/json" }

        expect(response).to have_http_status(:unprocessable_content)
      end
    end
  end

  describe "POST /api/v1/auth/sign_in" do
    let!(:user) { create(:user, email: "user@example.com", password: "password123") }

    context "with correct credentials" do
      it "returns a token" do
        post "/api/v1/auth/sign_in",
          params: { email: "user@example.com", password: "password123" }.to_json,
          headers: { "Content-Type" => "application/json" }

        expect(response).to have_http_status(:ok)
        expect(json_response[:token]).to be_present
        expect(json_response[:user][:email]).to eq("user@example.com")
      end
    end

    context "with wrong password" do
      it "returns unauthorized" do
        post "/api/v1/auth/sign_in",
          params: { email: "user@example.com", password: "wrongpass" }.to_json,
          headers: { "Content-Type" => "application/json" }

        expect(response).to have_http_status(:unauthorized)
        expect(json_response[:error]).to be_present
      end
    end

    context "with unknown email" do
      it "returns unauthorized" do
        post "/api/v1/auth/sign_in",
          params: { email: "nobody@example.com", password: "password123" }.to_json,
          headers: { "Content-Type" => "application/json" }

        expect(response).to have_http_status(:unauthorized)
      end
    end
  end
end
