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

  describe "GET /api/v1/transactions — paginação por cursor" do
    let!(:june_txn) do
      create(:transaction, user: user, account: account, category: category,
        occurred_on: Date.new(2026, 6, 15))
    end
    let!(:may_txn) do
      create(:transaction, user: user, account: account, category: category,
        occurred_on: Date.new(2026, 5, 10))
    end

    it "recorta a resposta em per_page itens e anuncia o próximo cursor" do
      get "/api/v1/transactions?per_page=1", headers: headers

      expect(response).to have_http_status(:ok)
      expect(json_response.length).to eq(1)
      expect(json_response.first[:id]).to eq(june_txn.id)
      expect(response.headers["X-Next-Cursor"]).to be_present
    end

    it "anuncia o tamanho nos headers" do
      get "/api/v1/transactions?per_page=1", headers: headers

      expect(response.headers["X-Per-Page"]).to eq("1")
    end

    it "entrega a página seguinte sem repetir a anterior" do
      get "/api/v1/transactions?per_page=1", headers: headers
      cursor = response.headers["X-Next-Cursor"]
      get "/api/v1/transactions?per_page=1&cursor=#{CGI.escape(cursor)}", headers: headers

      expect(json_response.length).to eq(1)
      expect(json_response.first[:id]).to eq(may_txn.id)
      expect(response.headers["X-Next-Cursor"]).to eq("")
    end

    # Cursor que o cliente guardou e ficou obsoleto — a aba passou a noite
    # aberta, os lançamentos daquela faixa sumiram — aponta para antes de tudo
    # que existe hoje. Janela vazia é resposta normal, não erro. Reenviar o
    # `X-Next-Cursor` vazio do fim não serve para testar isso: vazio e ausente
    # são a mesma coisa para a API, e o cliente para de pedir quando o recebe.
    it "devolve uma página vazia quando o cursor está além do fim" do
      esgotado = Base64.urlsafe_encode64("2000-01-01|1", padding: false)

      get "/api/v1/transactions?per_page=1&cursor=#{CGI.escape(esgotado)}", headers: headers

      expect(response).to have_http_status(:ok)
      expect(json_response).to eq([])
      expect(response.headers["X-Next-Cursor"]).to eq("")
    end

    it "mantém os filtros ao avançar pelo cursor" do
      get "/api/v1/transactions?year=2026&month=6&per_page=1", headers: headers

      expect(json_response.length).to eq(1)
      expect(json_response.first[:id]).to eq(june_txn.id)
    end

    it "usa 50 por página quando o cliente não pede tamanho" do
      get "/api/v1/transactions", headers: headers

      expect(response.headers["X-Per-Page"]).to eq("50")
      expect(json_response.length).to eq(2)
    end

    # per_page vem do cliente: sem teto, `per_page=999999` desfaz a proteção
    # que a paginação existe para dar.
    it "limita per_page ao teto mesmo se o cliente pedir mais" do
      get "/api/v1/transactions?per_page=9999", headers: headers

      expect(response.headers["X-Per-Page"]).to eq("200")
    end

    it "trata per_page inválido como o padrão" do
      get "/api/v1/transactions?per_page=abc", headers: headers

      expect(response.headers["X-Per-Page"]).to eq("50")
    end

    it "informa que o cursor corrompido é inválido" do
      get "/api/v1/transactions?cursor=nao-e-um-cursor", headers: headers

      expect(response).to have_http_status(:bad_request)
      expect(json_response[:error]).to eq("Cursor inválido")
    end

    it "não mascara ArgumentError que não vem da decodificação do cursor" do
      allow_any_instance_of(Api::V1::TransactionsController)
        .to receive(:paginate_by_cursor).and_raise(ArgumentError, "falha não relacionada ao cursor")

      expect {
        get "/api/v1/transactions", headers: headers
      }.to raise_error(ArgumentError, "falha não relacionada ao cursor")
    end

    it "expõe os headers de paginação ao navegador" do
      get "/api/v1/transactions", headers: headers.merge("Origin" => "http://localhost:3001")

      exposed = response.headers["Access-Control-Expose-Headers"].to_s
      expect(exposed).to include("X-Next-Cursor", "X-Per-Page")
    end

    it "recorta 120 lançamentos em 50 e não repete nem pula registros" do
      user.transactions.delete_all
      120.times do |index|
        create(:transaction, user: user, account: account, category: category,
          occurred_on: Date.new(2026, 1, 1) + index, description: "txn-#{index}")
      end

      ids = []
      cursor = nil
      loop do
        query = "per_page=50#{cursor ? "&cursor=#{CGI.escape(cursor)}" : ""}"
        get "/api/v1/transactions?#{query}", headers: headers
        ids.concat(json_response.map { |txn| txn[:id] })
        cursor = response.headers["X-Next-Cursor"].presence
        break unless cursor
      end

      expect(ids.length).to eq(120)
      expect(ids.uniq.length).to eq(ids.length)
      expect(ids).to eq(user.transactions.order(occurred_on: :desc, id: :desc).pluck(:id))
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

  # As 345 transações importadas antes do UR-2 ficaram sem conta. Enquanto
  # estiverem assim, saldo, caixa e patrimônio não fecham — e corrigir uma a uma
  # não é um pedido razoável.
  describe "POST /api/v1/transactions/assign_account" do
    let!(:orfas) do
      [
        create(:transaction, user: user, account: nil, occurred_on: "2026-06-01"),
        create(:transaction, user: user, account: nil, occurred_on: "2026-06-02")
      ]
    end

    it "returns 401 without token" do
      post "/api/v1/transactions/assign_account", params: { account_id: account.id }
      expect(response).to have_http_status(:unauthorized)
    end

    it "assigns the account to every orphan transaction" do
      post "/api/v1/transactions/assign_account", params: { account_id: account.id }.to_json, headers: headers

      expect(response).to have_http_status(:ok)
      expect(json_response[:updated]).to eq(2)
      expect(orfas.map { |t| t.reload.account_id }).to all(eq(account.id))
    end

    # Só as órfãs: quem já tem conta escolhida não é sobrescrito por uma ação
    # em massa disparada de um banner.
    it "does not touch transactions that already have an account" do
      outra = create(:account, user: user)
      ja_tem = create(:transaction, user: user, account: outra, occurred_on: "2026-06-03")

      post "/api/v1/transactions/assign_account", params: { account_id: account.id }.to_json, headers: headers

      expect(ja_tem.reload.account_id).to eq(outra.id)
      expect(json_response[:updated]).to eq(2)
    end

    it "rejects an account that belongs to someone else" do
      alheia = create(:account, user: create(:user))

      post "/api/v1/transactions/assign_account", params: { account_id: alheia.id }.to_json, headers: headers

      expect(response).to have_http_status(:unprocessable_entity)
      expect(orfas.map { |t| t.reload.account_id }).to all(be_nil)
    end

    it "rejects a missing account_id" do
      post "/api/v1/transactions/assign_account", headers: headers

      expect(response).to have_http_status(:unprocessable_entity)
      expect(orfas.first.reload.account_id).to be_nil
    end

    it "does not touch another user's orphan transactions" do
      alheia = create(:transaction, user: create(:user), account: nil, occurred_on: "2026-06-04")

      post "/api/v1/transactions/assign_account", params: { account_id: account.id }.to_json, headers: headers

      expect(alheia.reload.account_id).to be_nil
    end

    it "reports zero when there is nothing to fix" do
      orfas.each { |t| t.update!(account: account) }

      post "/api/v1/transactions/assign_account", params: { account_id: account.id }.to_json, headers: headers

      expect(json_response[:updated]).to eq(0)
    end
  end
end
