require "rails_helper"

RSpec.describe "Members API", type: :request do
  let(:user)    { create(:user) }
  let(:headers) { auth_headers_for(user) }

  describe "GET /api/v1/members" do
    let!(:members)  { create_list(:member, 3, user: user) }
    let!(:inactive) { create(:member, :inactive, user: user) }

    it "returns only active members" do
      get "/api/v1/members", headers: headers

      expect(response).to have_http_status(:ok)
      expect(json_response.length).to eq(3)
    end

    it "returns 401 without token" do
      get "/api/v1/members"
      expect(response).to have_http_status(:unauthorized)
    end
  end

  describe "GET /api/v1/members/:id" do
    let(:member) { create(:member, user: user) }

    it "returns the member" do
      get "/api/v1/members/#{member.id}", headers: headers

      expect(response).to have_http_status(:ok)
      expect(json_response[:id]).to eq(member.id)
    end

    it "returns 404 for another user's member" do
      other = create(:member, user: create(:user))
      get "/api/v1/members/#{other.id}", headers: headers

      expect(response).to have_http_status(:not_found)
    end
  end

  describe "POST /api/v1/members" do
    let(:valid_params) { { name: "Clarea Almeida", relationship: "titular" } }

    it "creates a member" do
      post "/api/v1/members", params: valid_params.to_json, headers: headers

      expect(response).to have_http_status(:created)
      expect(json_response[:name]).to eq("Clarea Almeida")
    end

    it "returns errors for invalid params" do
      post "/api/v1/members", params: { name: "" }.to_json, headers: headers

      expect(response).to have_http_status(:unprocessable_content)
      expect(json_response[:errors]).to be_present
    end
  end

  describe "PATCH /api/v1/members/:id" do
    let(:member) { create(:member, user: user, name: "Old") }

    it "updates the member" do
      patch "/api/v1/members/#{member.id}",
        params: { name: "New" }.to_json, headers: headers

      expect(response).to have_http_status(:ok)
      expect(json_response[:name]).to eq("New")
    end
  end

  describe "DELETE /api/v1/members/:id" do
    let(:member) { create(:member, user: user) }

    it "soft-deletes the member" do
      delete "/api/v1/members/#{member.id}", headers: headers

      expect(response).to have_http_status(:no_content)
      expect(member.reload.active).to be(false)
    end
  end
end
