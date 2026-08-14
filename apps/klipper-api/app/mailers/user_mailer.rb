class UserMailer < ApplicationMailer
  def password_reset(user, token)
    @user = user
    @reset_url = "#{frontend_base_url}/redefinir-senha?token=#{token}"
    mail(to: user.email, subject: "Redefinição de senha - Klipper")
  end

  private

  def frontend_base_url
    ENV.fetch("CORS_ORIGINS", "http://localhost:3001").split(",").first
  end
end
