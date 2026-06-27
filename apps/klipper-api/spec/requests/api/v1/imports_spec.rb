require 'rails_helper'

RSpec.describe "Api::V1::Imports", type: :request do
  let(:user) { create(:user) }
  let(:token) { JwtService.encode(user_id: user.id) }
  let(:auth_headers) { { "Authorization" => "Bearer #{token}" } }

  let(:csv_content) do
    <<~CSV
      Data,Descrição,Valor
      01/06/2026,COMPRA DÉBITO SUPERMERCADO EXTRA,-150.00
      05/06/2026,PIX RECEBIDO SALÁRIO,5000.00
      10/06/2026,COMPRA DÉBITO POSTO SHELL,-120.50
    CSV
  end
  let(:csv_file) { Rack::Test::UploadedFile.new(StringIO.new(csv_content), 'text/csv', original_filename: 'extrato.csv') }

  describe "POST /api/v1/imports" do
    it "returns 401 without token" do
      post "/api/v1/imports", params: { file: csv_file }
      expect(response).to have_http_status(:unauthorized)
    end

    it "creates transactions from CSV rows" do
      expect {
        post "/api/v1/imports",
          params: { file: csv_file },
          headers: auth_headers
      }.to change { user.transactions.count }.by(3)

      expect(response).to have_http_status(:ok)
    end

    it "returns import summary" do
      post "/api/v1/imports",
        params: { file: csv_file },
        headers: auth_headers

      json = JSON.parse(response.body)
      expect(json["imported"]).to eq(3)
      expect(json["errors"]).to eq([])
    end

    it "sets debit type for negative amounts" do
      post "/api/v1/imports",
        params: { file: csv_file },
        headers: auth_headers

      supermercado = user.transactions.find_by(description: "COMPRA DÉBITO SUPERMERCADO EXTRA")
      expect(supermercado.transaction_type).to eq("debit")
      expect(supermercado.amount).to eq(150.00)
    end

    it "sets credit type for positive amounts" do
      post "/api/v1/imports",
        params: { file: csv_file },
        headers: auth_headers

      salario = user.transactions.find_by(description: "PIX RECEBIDO SALÁRIO")
      expect(salario.transaction_type).to eq("credit")
      expect(salario.amount).to eq(5000.00)
    end

    it "auto-categorizes matching transactions" do
      create(:category, user: user, name: "Alimentação", category_type: "expense")
      post "/api/v1/imports",
        params: { file: csv_file },
        headers: auth_headers

      supermercado = user.transactions.find_by(description: "COMPRA DÉBITO SUPERMERCADO EXTRA")
      expect(supermercado.category).not_to be_nil
      expect(supermercado.category.name).to eq("Alimentação")
    end

    it "assigns account when account_id param provided" do
      account = create(:account, user: user)
      post "/api/v1/imports",
        params: { file: csv_file, account_id: account.id },
        headers: auth_headers

      expect(user.transactions.where(account: account).count).to eq(3)
    end

    it "returns 422 when no file provided" do
      post "/api/v1/imports", headers: auth_headers
      expect(response).to have_http_status(:unprocessable_entity)
    end
  end
end
