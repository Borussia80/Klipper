require 'rails_helper'

RSpec.describe "Api::V1::Imports", type: :request do
  let(:user) { create(:user) }
  let(:token) { JwtService.encode(user_id: user.id, token_version: user.token_version) }
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

    it "returns 422 without persisting anything when a PDF is sent to the CSV endpoint" do
      fake_pdf = Rack::Test::UploadedFile.new(StringIO.new("%PDF-1.4\nnão é um csv"), "application/pdf", original_filename: "fatura.pdf")

      expect {
        post "/api/v1/imports", params: { file: fake_pdf }, headers: auth_headers
      }.not_to change { user.transactions.count }

      expect(response).to have_http_status(:unprocessable_content)
      expect(JSON.parse(response.body)["error"]).to match(/não parece ser um CSV/)
    end

    it "returns 422 without persisting anything when the file is bigger than the allowed size" do
      oversized_content = "Data,Descrição,Valor\n" + ("01/06/2026,item,-10.00\n" * 1) + ("a" * (BankImport::FileGuard::MAX_BYTES + 1))
      oversized_file = Rack::Test::UploadedFile.new(StringIO.new(oversized_content), "text/csv", original_filename: "gigante.csv")

      expect {
        post "/api/v1/imports", params: { file: oversized_file }, headers: auth_headers
      }.not_to change { user.transactions.count }

      expect(response).to have_http_status(:unprocessable_content)
      expect(JSON.parse(response.body)["error"]).to match(/maior/)
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

    it "returns 422 without parsing anything when a CSV is sent to the PDF endpoint" do
      fake_csv = Rack::Test::UploadedFile.new(StringIO.new("Data,Descrição,Valor\n01/06/2026,item,-10.00\n"), "text/csv", original_filename: "extrato.csv")

      expect(PDF::Reader).not_to receive(:new)

      post "/api/v1/imports/preview", params: { file: fake_csv }, headers: auth_headers

      expect(response).to have_http_status(:unprocessable_content)
      expect(JSON.parse(response.body)["error"]).to match(/não é um PDF válido/)
    end
  end

  describe "POST /api/v1/imports/confirm" do
    let(:rows) do
      [
        signed_row(occurred_on: "2026-06-25", description: "JoaoEMaria", amount: "-37.50"),
        signed_row(occurred_on: "2026-06-10", description: "LOJADOIS", amount: "-15.50")
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

  describe "SEC-05: BOLA em account_id/member_id (cross-user) na importação" do
    let(:other_user)    { create(:user) }
    let(:other_account) { create(:account, user: other_user) }
    let(:other_member)  { create(:member, user: other_user) }
    let(:rows) do
      [
        signed_row(occurred_on: "2026-06-25", description: "JoaoEMaria", amount: "-37.50"),
        signed_row(occurred_on: "2026-06-10", description: "LOJADOIS", amount: "-15.50")
      ]
    end

    describe "POST /api/v1/imports (CSV)" do
      it "não vincula transações à account_id de outro usuário e reporta erro por linha" do
        expect {
          post "/api/v1/imports",
            params: { file: csv_file, account_id: other_account.id },
            headers: auth_headers
        }.not_to change { user.transactions.count }

        expect(response).to have_http_status(:ok)
        json = JSON.parse(response.body)
        expect(json["imported"]).to eq(0)
        expect(json["errors"].length).to eq(3)
        expect(json["errors"]).to all(include("Conta inválida"))
      end
    end

    describe "POST /api/v1/imports/confirm (PDF)" do
      it "não vincula transações à account_id de outro usuário e reporta erro por linha" do
        expect {
          post "/api/v1/imports/confirm",
            params: { rows: rows, account_id: other_account.id },
            headers: auth_headers
        }.not_to change { user.transactions.count }

        expect(response).to have_http_status(:ok)
        json = JSON.parse(response.body)
        expect(json["imported"]).to eq(0)
        expect(json["errors"].length).to eq(2)
        expect(json["errors"]).to all(include("Conta inválida"))
      end

      it "não vincula transações a member_id de outro usuário e reporta erro por linha" do
        rows_with_member = rows.map { |r| r.merge(member_id: other_member.id) }

        expect {
          post "/api/v1/imports/confirm",
            params: { rows: rows_with_member },
            headers: auth_headers
        }.not_to change { user.transactions.count }

        expect(response).to have_http_status(:ok)
        json = JSON.parse(response.body)
        expect(json["imported"]).to eq(0)
        expect(json["errors"].length).to eq(2)
        expect(json["errors"]).to all(include("Portador inválido"))
      end
    end
  end

  describe "SEC-17: assinatura por linha em imports/confirm" do
    let(:extrato_file) do
      Rack::Test::UploadedFile.new(pdf_fixture_path("itau_extrato.pdf").to_s, "application/pdf")
    end

    def preview_rows
      with_pdf_fixture("itau_extrato.pdf") do
        post "/api/v1/imports/preview", params: { file: extrato_file }, headers: auth_headers
      end
      JSON.parse(response.body)["rows"]
    end

    it "cada linha do preview inclui um token assinado" do
      rows = preview_rows

      expect(rows).not_to be_empty
      rows.each { |row| expect(row["token"]).to be_a(String) }
    end

    it "confirma o fluxo legítimo preview -> confirm e persiste os valores reais do documento" do
      rows = preview_rows
      first = rows.first

      post "/api/v1/imports/confirm", params: { rows: rows }, headers: auth_headers

      expect(response).to have_http_status(:ok)
      json = JSON.parse(response.body)
      expect(json["errors"]).to be_empty
      expect(json["imported"] + json["duplicates"]).to eq(rows.size)

      tx = user.transactions.find_by(description: first["description"])
      expect(tx.amount.to_s("F")).to eq(BigDecimal(first["amount"]).abs.to_s("F"))
    end

    it "adulterar amount/description/occurred_on no confirm não altera o que é persistido" do
      rows = preview_rows
      original = rows.first
      tampered = rows.dup
      tampered[0] = original.merge(
        "amount" => "-999999.00",
        "description" => "VALOR FORJADO",
        "occurred_on" => "2000-01-01"
      )

      post "/api/v1/imports/confirm", params: { rows: tampered }, headers: auth_headers

      expect(response).to have_http_status(:ok)
      json = JSON.parse(response.body)
      expect(json["errors"]).to be_empty
      expect(json["imported"] + json["duplicates"]).to eq(rows.size)

      persisted = user.transactions.find_by(description: original["description"])
      expect(persisted).to be_present
      expect(persisted.amount.to_s("F")).to eq(BigDecimal(original["amount"]).abs.to_s("F"))
      expect(user.transactions.find_by(description: "VALOR FORJADO")).to be_nil
    end

    it "rejeita e reporta erro de linha quando o token está ausente" do
      rows = preview_rows
      without_token = rows.dup
      without_token[0] = rows.first.except("token")

      post "/api/v1/imports/confirm", params: { rows: without_token }, headers: auth_headers

      json = JSON.parse(response.body)
      expect(json["errors"].size).to eq(1)
      expect(json["imported"] + json["duplicates"]).to eq(rows.size - 1)
    end

    it "expira o token após 30 minutos e rejeita a linha" do
      rows = preview_rows

      travel 31.minutes do
        expect {
          post "/api/v1/imports/confirm", params: { rows: rows }, headers: auth_headers
        }.not_to change { user.transactions.count }
      end

      json = JSON.parse(response.body)
      expect(json["imported"]).to eq(0)
      expect(json["errors"].size).to eq(rows.size)
    end
  end

  describe "audit logging" do
    it "creates an IMPORT_DATA audit log entry on successful CSV import" do
      expect {
        post "/api/v1/imports", params: { file: csv_file }, headers: auth_headers
      }.to change { AuditLog.where(event_type: "IMPORT_DATA", status: "success").count }.by(1)

      log = AuditLog.last
      expect(log.user_id).to eq(user.id)
      expect(log.record_count).to eq(3)
      expect(log.event_type).to eq("IMPORT_DATA")
      expect(log.status).to eq("success")
    end

    it "creates an IMPORT_DATA audit log entry on successful PDF confirm" do
      rows = [
        signed_row(occurred_on: "2026-06-25", description: "JoaoEMaria", amount: "-37.50"),
        signed_row(occurred_on: "2026-06-10", description: "LOJADOIS", amount: "-15.50")
      ]

      expect {
        post "/api/v1/imports/confirm", params: { rows: rows }, headers: auth_headers
      }.to change { AuditLog.where(event_type: "IMPORT_DATA", status: "success").count }.by(1)

      log = AuditLog.last
      expect(log.user_id).to eq(user.id)
      expect(log.record_count).to eq(2)
      expect(log.event_type).to eq("IMPORT_DATA")
      expect(log.status).to eq("success")
    end

    it "creates a failure audit log when CSV import has errors" do
      expect {
        post "/api/v1/imports", params: { file: csv_file, account_id: 99999 }, headers: auth_headers
      }.to change { AuditLog.where(event_type: "IMPORT_DATA", status: "failure").count }.by(1)

      log = AuditLog.last
      expect(log.user_id).to eq(user.id)
      expect(log.record_count).to eq(0)
      expect(log.event_type).to eq("IMPORT_DATA")
      expect(log.status).to eq("failure")
    end

    it "creates a failure audit log when PDF confirm has errors" do
      rows = [
        signed_row(occurred_on: "2026-06-25", description: "JoaoEMaria", amount: "-37.50"),
        signed_row(occurred_on: "2026-06-10", description: "LOJADOIS", amount: "-15.50")
      ]
      rows_without_token = rows.map { |r| r.except("token") }

      expect {
        post "/api/v1/imports/confirm", params: { rows: rows_without_token }, headers: auth_headers
      }.to change { AuditLog.where(event_type: "IMPORT_DATA", status: "failure").count }.by(1)

      log = AuditLog.last
      expect(log.user_id).to eq(user.id)
      expect(log.event_type).to eq("IMPORT_DATA")
      expect(log.status).to eq("failure")
    end
  end
end
