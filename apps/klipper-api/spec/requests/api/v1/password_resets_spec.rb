require "rails_helper"

RSpec.describe "Api::V1::PasswordResets", type: :request do
  let(:user) { create(:user, email: "roberto@example.com", password: "secret123", password_confirmation: "secret123") }

  describe "POST /api/v1/password_resets" do
    it "sends a reset e-mail when the address exists" do
      expect { post "/api/v1/password_resets", params: { email: user.email } }
        .to change { ActionMailer::Base.deliveries.count }.by(1)

      expect(response).to have_http_status(:ok)
      mail = ActionMailer::Base.deliveries.last
      expect(mail.to).to eq([ user.email ])
      expect(mail.body.encoded).to match(%r{/redefinir-senha\?token=})
    end

    it "returns the same generic message and sends no e-mail for an unknown address" do
      user # ensure a user exists, just not the one we're requesting

      expect { post "/api/v1/password_resets", params: { email: "nobody@example.com" } }
        .not_to change { ActionMailer::Base.deliveries.count }

      expect(response).to have_http_status(:ok)
      expect(json_response[:message]).to eq("Se o e-mail existir, enviaremos um link de redefinição.")
    end
  end

  describe "PATCH /api/v1/password_resets/:token" do
    it "resets the password and revokes existing tokens when the token is valid" do
      token = user.generate_token_for(:password_reset)

      expect {
        patch "/api/v1/password_resets/#{token}",
          params: { password: "newpass456", password_confirmation: "newpass456" }
      }.to change { user.reload.token_version }.by(1)

      expect(response).to have_http_status(:ok)
      expect(user.reload.authenticate("newpass456")).to be_truthy
    end

    it "returns 422 for a garbage token" do
      patch "/api/v1/password_resets/not-a-real-token",
        params: { password: "newpass456", password_confirmation: "newpass456" }

      expect(response).to have_http_status(:unprocessable_content)
      expect(json_response[:error]).to match(/inválido ou expirado/)
    end

    it "returns 422 once the token has expired" do
      token = user.generate_token_for(:password_reset)

      travel 31.minutes do
        patch "/api/v1/password_resets/#{token}",
          params: { password: "newpass456", password_confirmation: "newpass456" }
      end

      expect(response).to have_http_status(:unprocessable_content)
      expect(user.reload.authenticate("newpass456")).to be_falsey
    end

    it "returns 422 with validation errors when the confirmation doesn't match" do
      token = user.generate_token_for(:password_reset)

      patch "/api/v1/password_resets/#{token}",
        params: { password: "newpass456", password_confirmation: "somethingelse" }

      expect(response).to have_http_status(:unprocessable_content)
      expect(json_response[:errors]).to be_present
    end

    it "invalidates the token once it has been used" do
      token = user.generate_token_for(:password_reset)

      patch "/api/v1/password_resets/#{token}",
        params: { password: "newpass456", password_confirmation: "newpass456" }

      patch "/api/v1/password_resets/#{token}",
        params: { password: "anotherpass789", password_confirmation: "anotherpass789" }

      expect(response).to have_http_status(:unprocessable_content)
      expect(user.reload.authenticate("newpass456")).to be_truthy
    end
  end
end
