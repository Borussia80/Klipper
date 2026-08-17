require "rails_helper"

RSpec.describe "Transactions API", type: :request do
  let(:user)    { create(:user) }
  let(:headers) { auth_headers_for(user) }
  let(:account)  { create(:account, user: user) }
  let(:category) { create(:category, user: user, icon: "food") }

  describe "GET /api/v1/transactions" do
    let!(:june_txn) do
      create(:transaction, user: user, account: account, category: category,
        occurred_on: Date.new(2026, 6, 15))
    end
    let!(:may_txn) do
      create(:transaction, user: user, account: account, category: category,
        occurred_on: Date.new(2026, 5, 10))
    end

    it "returns all transactions for current user" do
      get "/api/v1/transactions", headers: headers
      expect(response).to have_http_status(:ok)
      expect(json_response.length).to eq(2)
    end

    it "filters by year and month" do
      get "/api/v1/transactions?year=2026&month=6", headers: headers
      expect(json_response.length).to eq(1)
      expect(json_response.first[:id]).to eq(june_txn.id)
    end

    it "filters by account_id" do
      other_account = create(:account, user: user)
      create(:transaction, user: user, account: other_account, category: category)
      get "/api/v1/transactions?account_id=#{account.id}", headers: headers
      ids = json_response.map { |t| t[:id] }
      expect(ids).to include(june_txn.id, may_txn.id)
      expect(ids.length).to eq(2)
    end

    it "filters by member_id" do
      member = create(:member, user: user)
      other_member = create(:member, user: user)
      create(:transaction, user: user, account: account, category: category, member: other_member)
      create(:transaction, user: user, account: account, category: category, member: member)

      get "/api/v1/transactions?member_id=#{member.id}", headers: headers
      ids = json_response.map { |t| t[:id] }

      expect(ids.length).to eq(1)
    end

    it "returns 401 without token" do
      get "/api/v1/transactions"
      expect(response).to have_http_status(:unauthorized)
    end
  end

  describe "GET /api/v1/transactions/:id" do
    let(:txn) { create(:transaction, user: user, account: account, category: category) }

    it "returns the transaction" do
      get "/api/v1/transactions/#{txn.id}", headers: headers
      expect(response).to have_http_status(:ok)
      expect(json_response[:id]).to eq(txn.id)
    end

    it "returns 404 for another user's transaction" do
      other = create(:transaction, user: create(:user),
        account: create(:account, user: create(:user)),
        category: create(:category, user: create(:user), icon: "x"))
      get "/api/v1/transactions/#{other.id}", headers: headers
      expect(response).to have_http_status(:not_found)
    end
  end

  describe "POST /api/v1/transactions" do
    let(:valid_params) do
      {
        account_id: account.id,
        category_id: category.id,
        description: "Compra no mercado",
        amount: 150.0,
        transaction_type: "debit",
        occurred_on: "2026-06-20"
      }
    end

    it "creates a transaction" do
      post "/api/v1/transactions", params: valid_params.to_json, headers: headers
      expect(response).to have_http_status(:created)
      expect(json_response[:description]).to eq("Compra no mercado")
    end

    it "auto-categorizes when no category_id given" do
      create(:category, user: user, name: "Alimentação", category_type: "expense", icon: "food")
      params = valid_params.except(:category_id).merge(description: "Supermercado Extra")
      post "/api/v1/transactions", params: params.to_json, headers: headers
      expect(response).to have_http_status(:created)
      expect(json_response[:category_id]).not_to be_nil
    end

    it "returns errors for invalid params" do
      post "/api/v1/transactions", params: { account_id: account.id, amount: -1 }.to_json, headers: headers
      expect(response).to have_http_status(:unprocessable_content)
    end

    it "rejects a future occurred_on and does not persist the transaction" do
      future_params = valid_params.merge(occurred_on: (Time.zone.today + 1).to_s)
      expect do
        post "/api/v1/transactions", params: future_params.to_json, headers: headers
      end.not_to change(Transaction, :count)
      expect(response).to have_http_status(:unprocessable_content)
    end
  end

  describe "PATCH /api/v1/transactions/:id" do
    let(:txn) { create(:transaction, user: user, account: account, category: category, description: "Old") }

    it "updates the transaction" do
      patch "/api/v1/transactions/#{txn.id}",
        params: { description: "New" }.to_json, headers: headers
      expect(response).to have_http_status(:ok)
      expect(json_response[:description]).to eq("New")
    end
  end

  describe "SEC-04: BOLA em account_id/category_id/member_id (cross-user)" do
    let(:other_user)     { create(:user) }
    let(:other_account)  { create(:account, user: other_user) }
    let(:other_category) { create(:category, user: other_user, icon: "x") }
    let(:other_member)   { create(:member, user: other_user) }

    it "rejects account_id de outro usuário na criação" do
      post "/api/v1/transactions",
        params: { account_id: other_account.id, category_id: category.id, description: "x",
                   amount: 10, transaction_type: "debit", occurred_on: "2026-06-20" }.to_json,
        headers: headers
      expect(response).to have_http_status(:unprocessable_content)
    end

    it "rejects category_id de outro usuário na criação" do
      post "/api/v1/transactions",
        params: { account_id: account.id, category_id: other_category.id, description: "x",
                   amount: 10, transaction_type: "debit", occurred_on: "2026-06-20" }.to_json,
        headers: headers
      expect(response).to have_http_status(:unprocessable_content)
    end

    it "rejects member_id de outro usuário na criação" do
      post "/api/v1/transactions",
        params: { account_id: account.id, category_id: category.id, member_id: other_member.id,
                   description: "x", amount: 10, transaction_type: "debit", occurred_on: "2026-06-20" }.to_json,
        headers: headers
      expect(response).to have_http_status(:unprocessable_content)
    end

    it "rejects account_id de outro usuário na atualização (não passa a somar nos totais da conta alheia)" do
      txn = create(:transaction, user: user, account: account, category: category)
      patch "/api/v1/transactions/#{txn.id}",
        params: { account_id: other_account.id }.to_json, headers: headers
      expect(response).to have_http_status(:unprocessable_content)
      expect(txn.reload.account_id).to eq(account.id)
    end

    it "rejects member_id de outro usuário na atualização" do
      txn = create(:transaction, user: user, account: account, category: category)
      patch "/api/v1/transactions/#{txn.id}",
        params: { member_id: other_member.id }.to_json, headers: headers
      expect(response).to have_http_status(:unprocessable_content)
      expect(txn.reload.member_id).to be_nil
    end
  end

  describe "DELETE /api/v1/transactions/:id" do
    let(:txn) { create(:transaction, user: user, account: account, category: category) }

    it "destroys the transaction" do
      delete "/api/v1/transactions/#{txn.id}", headers: headers
      expect(response).to have_http_status(:no_content)
      expect { txn.reload }.to raise_error(ActiveRecord::RecordNotFound)
    end
  end
end
