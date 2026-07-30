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

      it "seeds default categories so the user isn't starting from a blank slate" do
        post "/api/v1/auth/sign_up", params: valid_params.to_json,
          headers: { "Content-Type" => "application/json" }

        user = User.find_by(email: "new@example.com")
        expect(user.categories.pluck(:name)).to include("Alimentação", "Moradia", "Renda")
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

        decoded = JwtService.decode(json_response[:token])
        expect(decoded[:token_version]).to eq(user.token_version)
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

  describe "SEC-16: sign_in em tempo constante (sem vazar por timing se o e-mail existe)" do
    it "runs a bcrypt comparison even when the e-mail doesn't exist" do
      expect_any_instance_of(User).to receive(:authenticate).and_call_original

      post "/api/v1/auth/sign_in",
        params: { email: "nobody@example.com", password: "whatever" }.to_json,
        headers: { "Content-Type" => "application/json" }

      expect(response).to have_http_status(:unauthorized)
    end
  end

  describe "SEC-08: throttle de força bruta" do
    it "returns 429 after 5 sign_in attempts for the same e-mail within a minute" do
      5.times do
        post "/api/v1/auth/sign_in",
          params: { email: "victim@example.com", password: "wrongpass" }.to_json,
          headers: { "Content-Type" => "application/json" }
      end

      post "/api/v1/auth/sign_in",
        params: { email: "victim@example.com", password: "wrongpass" }.to_json,
        headers: { "Content-Type" => "application/json" }

      expect(response).to have_http_status(:too_many_requests)
      expect(json_response[:error]).to be_present
    end

    it "does not throttle sign_in attempts for a different e-mail" do
      5.times do
        post "/api/v1/auth/sign_in",
          params: { email: "victim@example.com", password: "wrongpass" }.to_json,
          headers: { "Content-Type" => "application/json" }
      end

      post "/api/v1/auth/sign_in",
        params: { email: "someone-else@example.com", password: "wrongpass" }.to_json,
        headers: { "Content-Type" => "application/json" }

      expect(response).to have_http_status(:unauthorized)
    end

    it "returns 429 after 20 auth requests from the same IP within a minute" do
      20.times do |i|
        post "/api/v1/auth/sign_in",
          params: { email: "attacker#{i}@example.com", password: "wrongpass" }.to_json,
          headers: { "Content-Type" => "application/json" }
      end

      post "/api/v1/auth/sign_in",
        params: { email: "attacker21@example.com", password: "wrongpass" }.to_json,
        headers: { "Content-Type" => "application/json" }

      expect(response).to have_http_status(:too_many_requests)
    end
  end
end
