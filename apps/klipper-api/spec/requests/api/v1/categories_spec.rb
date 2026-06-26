require "rails_helper"

RSpec.describe "Categories API", type: :request do
  let(:user)    { create(:user) }
  let(:headers) { auth_headers_for(user) }

  describe "GET /api/v1/categories" do
    let!(:categories) { create_list(:category, 3, user: user) }
    let!(:inactive)   { create(:category, :inactive, user: user) }

    it "returns only active categories" do
      get "/api/v1/categories", headers: headers

      expect(response).to have_http_status(:ok)
      expect(json_response.length).to eq(3)
    end

    it "returns 401 without token" do
      get "/api/v1/categories"
      expect(response).to have_http_status(:unauthorized)
    end
  end

  describe "GET /api/v1/categories/:id" do
    let(:category) { create(:category, user: user) }

    it "returns the category" do
      get "/api/v1/categories/#{category.id}", headers: headers

      expect(response).to have_http_status(:ok)
      expect(json_response[:id]).to eq(category.id)
    end

    it "returns 404 for another user's category" do
      other = create(:category, user: create(:user))
      get "/api/v1/categories/#{other.id}", headers: headers

      expect(response).to have_http_status(:not_found)
    end
  end

  describe "POST /api/v1/categories" do
    let(:valid_params) { { name: "Restaurantes", icon: "restaurant", category_type: "expense" } }

    it "creates a category" do
      post "/api/v1/categories", params: valid_params.to_json, headers: headers

      expect(response).to have_http_status(:created)
      expect(json_response[:name]).to eq("Restaurantes")
    end

    it "returns errors for invalid params" do
      post "/api/v1/categories", params: { name: "" }.to_json, headers: headers

      expect(response).to have_http_status(:unprocessable_entity)
      expect(json_response[:errors]).to be_present
    end
  end

  describe "PATCH /api/v1/categories/:id" do
    let(:category) { create(:category, user: user, name: "Old") }

    it "updates the category" do
      patch "/api/v1/categories/#{category.id}",
        params: { name: "New" }.to_json, headers: headers

      expect(response).to have_http_status(:ok)
      expect(json_response[:name]).to eq("New")
    end
  end

  describe "DELETE /api/v1/categories/:id" do
    let(:category) { create(:category, user: user) }

    it "soft-deletes the category" do
      delete "/api/v1/categories/#{category.id}", headers: headers

      expect(response).to have_http_status(:no_content)
      expect(category.reload.active).to be(false)
    end
  end
end
