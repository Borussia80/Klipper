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
