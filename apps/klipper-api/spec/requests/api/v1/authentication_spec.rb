require "rails_helper"

# O portão do BaseController, exercitado por uma rota protegida qualquer.
# A revogação por token_version já é coberta em users_spec.rb; aqui o assunto é
# o token_type, que separa "renovar sessão" de "autorizar requisição" (ARCH-001).
RSpec.describe "Authentication gate", type: :request do
  let(:user) { create(:user) }

  it "authenticates with an access token" do
    token = JwtService.encode(user_id: user.id, token_version: user.token_version)

    get "/api/v1/accounts", headers: { "Authorization" => "Bearer #{token}" }

    expect(response).to have_http_status(:ok)
  end

  # O refresh token vale 30 dias e existe só para trocar por um access token em
  # /api/v1/auth/refresh. Aceitá-lo como Bearer tornava o teto de 15 minutos do
  # access token decorativo para quem tivesse o cookie.
  it "rejects a refresh token used as a bearer token" do
    token = JwtService.encode_refresh(user_id: user.id, token_version: user.token_version)

    get "/api/v1/accounts", headers: { "Authorization" => "Bearer #{token}" }

    expect(response).to have_http_status(:unauthorized)
  end

  # Allowlist, não denylist: o que não se identifica como access não entra.
  # Cobre tanto os tokens emitidos antes do token_type existir quanto qualquer
  # tipo novo que venha a ser emitido pelo JwtService.encode.
  it "rejects a token that carries no token_type" do
    token = JWT.encode(
      { user_id: user.id, token_version: user.token_version, exp: 15.minutes.from_now.to_i },
      Rails.application.secret_key_base,
      "HS256",
    )

    get "/api/v1/accounts", headers: { "Authorization" => "Bearer #{token}" }

    expect(response).to have_http_status(:unauthorized)
  end

  it "rejects a token whose token_type is unknown" do
    token = JwtService.encode({ user_id: user.id, token_version: user.token_version }, token_type: "preview")

    get "/api/v1/accounts", headers: { "Authorization" => "Bearer #{token}" }

    expect(response).to have_http_status(:unauthorized)
  end
end
