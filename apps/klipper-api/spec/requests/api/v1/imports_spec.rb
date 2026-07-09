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

    it "ignores duplicates and reports them when the same CSV is imported twice" do
      post "/api/v1/imports", params: { file: csv_file }, headers: auth_headers
      second_upload = Rack::Test::UploadedFile.new(StringIO.new(csv_content), 'text/csv', original_filename: 'extrato.csv')
      post "/api/v1/imports", params: { file: second_upload }, headers: auth_headers

      json = JSON.parse(response.body)
      expect(json["imported"]).to eq(0)
      expect(json["duplicates"]).to eq(3)
      expect(user.transactions.count).to eq(3)
    end

    it "returns 422 when no file provided" do
      post "/api/v1/imports", headers: auth_headers
      expect(response).to have_http_status(:unprocessable_content)
    end
  end

  describe "POST /api/v1/imports/preview" do
    let(:extrato_file) do
      Rack::Test::UploadedFile.new(pdf_fixture_path("itau_extrato.pdf").to_s, "application/pdf")
    end
    let(:unrecognized_pdf) do
      Rack::Test::UploadedFile.new(StringIO.new("%PDF-1.4\nnão é um layout conhecido"), "application/pdf", original_filename: "estranho.pdf")
    end

    it "returns 401 without token" do
      post "/api/v1/imports/preview", params: { file: unrecognized_pdf }
      expect(response).to have_http_status(:unauthorized)
    end

    it "returns 422 when no file provided" do
      post "/api/v1/imports/preview", headers: auth_headers
      expect(response).to have_http_status(:unprocessable_content)
    end

    it "extrai e devolve as linhas do extrato Itaú sem persistir nenhuma transação" do
      with_pdf_fixture("itau_extrato.pdf") do
        expect {
          post "/api/v1/imports/preview",
            params: { file: extrato_file },
            headers: auth_headers
        }.not_to change { user.transactions.count }

        expect(response).to have_http_status(:ok)
        json = JSON.parse(response.body)
        expect(json["adapter"]).to eq("itau_extrato")
        expect(json["rows"]).not_to be_empty
        expect(json["warnings"]).to be_an(Array)
      end
    end

    it "returns 422 with an error message when the PDF layout isn't recognized" do
      allow(PDF::Reader).to receive(:new).and_raise(PDF::Reader::MalformedPDFError, "não é PDF")

      post "/api/v1/imports/preview",
        params: { file: unrecognized_pdf },
        headers: auth_headers

      expect(response).to have_http_status(:unprocessable_content)
      json = JSON.parse(response.body)
      expect(json["error"]).to be_present
    end
  end

  describe "POST /api/v1/imports/confirm" do
    let(:rows) do
      [
        { occurred_on: "2026-06-25", description: "JoaoEMaria", amount: "-37.50" },
        { occurred_on: "2026-06-10", description: "LOJADOIS", amount: "-15.50" }
      ]
    end

    it "returns 401 without token" do
      post "/api/v1/imports/confirm", params: { rows: rows }
      expect(response).to have_http_status(:unauthorized)
    end

    it "creates transactions from the confirmed rows" do
      expect {
        post "/api/v1/imports/confirm",
          params: { rows: rows },
          headers: auth_headers
      }.to change { user.transactions.count }.by(2)

      expect(response).to have_http_status(:ok)
      json = JSON.parse(response.body)
      expect(json["imported"]).to eq(2)
      expect(json["errors"]).to eq([])
    end

    it "assigns account when account_id param provided" do
      account = create(:account, user: user)

      post "/api/v1/imports/confirm",
        params: { rows: rows, account_id: account.id },
        headers: auth_headers

      expect(user.transactions.where(account: account).count).to eq(2)
    end

    it "returns 200 with imported: 0 when rows is empty" do
      post "/api/v1/imports/confirm", params: { rows: [] }, headers: auth_headers

      expect(response).to have_http_status(:ok)
      json = JSON.parse(response.body)
      expect(json["imported"]).to eq(0)
    end

    it "ignores duplicates and reports them when the same rows are confirmed twice" do
      post "/api/v1/imports/confirm", params: { rows: rows }, headers: auth_headers
      post "/api/v1/imports/confirm", params: { rows: rows }, headers: auth_headers

      json = JSON.parse(response.body)
      expect(json["imported"]).to eq(0)
      expect(json["duplicates"]).to eq(2)
      expect(user.transactions.count).to eq(2)
    end
  end
end
