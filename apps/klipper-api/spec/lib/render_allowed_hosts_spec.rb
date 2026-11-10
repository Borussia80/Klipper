require "spec_helper"
require "yaml"
require "action_dispatch"
require_relative "../../lib/allowed_hosts"

# O proxy /api/** da Vercel repassa o domínio do front em X-Forwarded-Host, e o
# HostAuthorization do Rails valida esse host. Sem os domínios do front na
# lista, todo POST pelo proxy vira 403 vazio em produção.
RSpec.describe "RAILS_ALLOWED_HOSTS declarado no render.yaml" do
  let(:render_hosts) do
    blueprint = YAML.load_file(File.expand_path("../../render.yaml", __dir__))
    env_vars = blueprint.fetch("services").find { |s| s["name"] == "klipper-api" }.fetch("envVars")
    env_vars.find { |v| v["key"] == "RAILS_ALLOWED_HOSTS" }&.fetch("value")
  end

  def status_through_host_authorization(hosts, forwarded_host)
    app = ActionDispatch::HostAuthorization.new(
      ->(_env) { [ 200, {}, [ "ok" ] ] },
      AllowedHosts.from_env(hosts),
      response_app: ->(_env) { [ 403, {}, [] ] }
    )
    env = Rack::MockRequest.env_for(
      "https://klipper-api.onrender.com/api/v1/auth/sign_in",
      method: "POST",
      "HTTP_X_FORWARDED_HOST" => forwarded_host
    )
    app.call(env).first
  end

  %w[klipper.quebec.com.br www.klipper.quebec.com.br klipper-app.vercel.app].each do |front_host|
    it "aceita POST repassado pelo proxy com X-Forwarded-Host #{front_host}" do
      expect(status_through_host_authorization(render_hosts, front_host)).to eq(200)
    end
  end

  it "bloqueia o mesmo POST quando a lista só tem o host da API" do
    expect(status_through_host_authorization("klipper-api.onrender.com", "klipper.quebec.com.br")).to eq(403)
  end
end
