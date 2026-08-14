require "rails_helper"

RSpec.describe "GET /api/v1/health", type: :request do
  it "returns ok status" do
    get "/api/v1/health"

    expect(response).to have_http_status(:ok)
    expect(json_response[:status]).to eq("ok")
    expect(json_response[:env]).to eq("test")
    expect(json_response[:timestamp]).to be_present
  end
end

RSpec.describe Api::V1::HealthController, ".excluded_from_ssl_redirect?" do
  it "excludes the health check path from the SEC-09 force_ssl redirect" do
    request = instance_double(ActionDispatch::Request, path: "/api/v1/health")
    expect(described_class.excluded_from_ssl_redirect?(request)).to eq(true)
  end

  it "does not exclude other paths" do
    request = instance_double(ActionDispatch::Request, path: "/api/v1/users/me")
    expect(described_class.excluded_from_ssl_redirect?(request)).to eq(false)
  end
end
