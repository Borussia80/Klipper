require "rails_helper"

RSpec.describe UserMailer, type: :mailer do
  let(:user) { build(:user, email: "roberto@example.com") }

  around do |example|
    original_origin = ENV["CORS_ORIGINS"]
    example.run
  ensure
    original_origin.nil? ? ENV.delete("CORS_ORIGINS") : ENV["CORS_ORIGINS"] = original_origin
  end

  describe "password_reset" do
    it "uses the local frontend URL when CORS_ORIGINS is unset" do
      ENV.delete("CORS_ORIGINS")

      mail = described_class.password_reset(user, "reset-token")

      expect(mail.body.encoded).to include("http://localhost:3000/redefinir-senha?token=reset-token")
    end

    it "uses the first configured CORS origin" do
      ENV["CORS_ORIGINS"] = "https://a.example,https://b.example"

      mail = described_class.password_reset(user, "reset-token")

      expect(mail.body.encoded).to include("https://a.example/redefinir-senha?token=reset-token")
      expect(mail.body.encoded).not_to include("https://b.example/redefinir-senha")
    end
  end
end
