require "rails_helper"

RSpec.describe CsvImportService, type: :service do
  let(:user) { create(:user) }

  let(:csv_content) do
    <<~CSV
      Data,Descrição,Valor
      01/06/2026,COMPRA DÉBITO SUPERMERCADO EXTRA,-150.00
      05/06/2026,PIX RECEBIDO SALÁRIO,5000.00
      10/06/2026,COMPRA DÉBITO POSTO SHELL,-120.50
    CSV
  end

  def run(content, account_id: nil)
    described_class.new(user, StringIO.new(content), account_id: account_id).call
  end

  def preview(content, account_id: nil)
    described_class.new(user, StringIO.new(content), account_id: account_id).preview
  end

  describe "#preview" do
    let(:nubank_csv_content) do
      <<~CSV
        Data,Valor,Identificador,Descrição
        01/06/2026,-5000.91,id-1,PIX TRANSF JOSE TESTE DA SILVA
        02/06/2026,100.00,id-2,RENDIMENTO CONTA
        03/06/2026,-42.50,id-3,COMPRA MERCADO
        04/06/2026,250.25,id-4,PIX RECEBIDO
      CSV
    end

    it "serializes Nubank rows with signed tokens without persisting transactions" do
      expect {
        @result = preview(nubank_csv_content)
      }.not_to change { user.transactions.count }

      expect(@result).to have_attributes(adapter: "csv", warnings: [])
      expect(@result.rows.size).to eq(4)
      expect(@result.rows).to all(include(:token))
      expect(@result.rows.first).to include(
        occurred_on: "2026-06-01", description: "PIX TRANSF JOSE TESTE DA SILVA", amount: "-5000.91"
      )
    end

    it "turns invalid rows into line warnings and keeps valid rows" do
      content = <<~CSV
        Data,Valor,Identificador,Descrição
        01/06/2026,-10.00,id-1,COMPRA VALIDA
        31/13/2026,-20.00,id-2,DATA INVALIDA
        03/06/2026,valor,id-3,VALOR INVALIDO
        04/06/2026,,-4,DADO INCOMPLETO
      CSV

      result = preview(content)

      expect(result.rows.map { |row| row[:description] }).to eq([ "COMPRA VALIDA" ])
      expect(result.warnings).to eq([
        { page: 3, reason: "Data inválida: 31/13/2026" },
        { page: 4, reason: "Valor inválido: valor" },
        { page: 5, reason: "Dados incompletos" }
      ])
    end

    it "returns a clear error when no known columns are found" do
      result = preview("Foo,Bar,Baz\n1,2,3\n")

      expect(result.error?).to eq(true)
      expect(result.error).to match(/colunas reconhecidas/)
    end

    it "suggests an own transfer when the user has an identity and a matching counterpart" do
      user.update!(own_names: [ "Jose Teste Da Silva" ], own_cpf_mask: "123.456")
      other_account = create(:account, user: user)
      create(:transaction, user:, account: other_account, description: "PIX recebido Jose Teste Da Silva 123.456",
             amount: 5000.91, transaction_type: "credit", occurred_on: Date.new(2026, 6, 1))

      result = preview(nubank_csv_content)

      expect(result.rows.first[:own_transfer]).to eq(state: "paired", counterpart: "existing")
    end

    it "keeps own_transfer nil when the user has no identity" do
      result = preview(nubank_csv_content)

      expect(result.rows.first[:own_transfer]).to be_nil
    end
  end

  it "imports every valid row and reports zero errors" do
    result = run(csv_content)
    expect(result.imported).to eq(3)
    expect(result.errors).to eq([])
  end

  it "sets debit type and absolute amount for negative values" do
    run(csv_content)
    tx = user.transactions.find_by(description: "COMPRA DÉBITO SUPERMERCADO EXTRA")
    expect(tx.transaction_type).to eq("debit")
    expect(tx.amount).to eq(150.00)
  end

  it "sets credit type and absolute amount for positive values" do
    run(csv_content)
    tx = user.transactions.find_by(description: "PIX RECEBIDO SALÁRIO")
    expect(tx.transaction_type).to eq("credit")
    expect(tx.amount).to eq(5000.00)
  end

  it "auto-categorizes matching descriptions" do
    create(:category, user: user, name: "Alimentação", category_type: "expense")
    run(csv_content)
    tx = user.transactions.find_by(description: "COMPRA DÉBITO SUPERMERCADO EXTRA")
    expect(tx.category&.name).to eq("Alimentação")
  end

  it "assigns the given account_id to every imported transaction" do
    account = create(:account, user: user)
    run(csv_content, account_id: account.id)
    expect(user.transactions.where(account: account).count).to eq(3)
  end

  it "collects a per-row error for an invalid date without stopping the import" do
    content = <<~CSV
      Data,Descrição,Valor
      31/13/2026,COMPRA INVALIDA,-10.00
      01/06/2026,COMPRA VALIDA,-20.00
    CSV
    result = run(content)
    expect(result.imported).to eq(1)
    expect(result.errors.first).to match(/Linha 2: Data inválida/)
  end

  it "collects a per-row error for an incomplete row without stopping the import" do
    content = <<~CSV
      Data,Descrição,Valor
      01/06/2026,,-10.00
      05/06/2026,COMPRA VALIDA,-20.00
    CSV
    result = run(content)
    expect(result.imported).to eq(1)
    expect(result.errors.first).to match(/Linha 2: Dados incompletos/)
  end

  it "returns a single error for a malformed CSV instead of raising" do
    result = run(%("unterminated))
    expect(result.imported).to eq(0)
    expect(result.errors.first).to match(/CSV inválido/)
  end

  it "reports zero duplicates on a first-time import" do
    result = run(csv_content)
    expect(result.duplicates).to eq(0)
  end

  it "ignores duplicate rows and reports them separately when the same CSV is imported twice" do
    run(csv_content)
    result = run(csv_content)

    expect(result.imported).to eq(0)
    expect(result.duplicates).to eq(3)
    expect(user.transactions.count).to eq(3)
  end

  it "imports identical rows with separate ordinals and dedupes them on reimport" do
    account = create(:account, user: user)
    content = <<~CSV
      Data,Descrição,Valor
      01/06/2026,CAFÉ X,-5.00
      01/06/2026,CAFE X,-5.00
    CSV

    first = run(content, account_id: account.id)
    second = run(content, account_id: account.id)

    expect(first).to have_attributes(imported: 2, duplicates: 0)
    expect(second).to have_attributes(imported: 0, duplicates: 2)
    expect(user.transactions.where(account: account).pluck(:external_id).uniq.size).to eq(2)
  end

  it "only counts as duplicate the rows that match an existing transaction, importing the rest" do
    run(csv_content)
    extra_content = csv_content + "15/06/2026,COMPRA NOVA LOJA,-30.00\n"

    result = run(extra_content)

    expect(result.imported).to eq(1)
    expect(result.duplicates).to eq(3)
  end

  context "with a different CSV export format (semicolon delimiter, English headers, ISO date)" do
    let(:alt_csv_content) do
      <<~CSV
        Date;Description;Amount
        2026-06-01;COMPRA DEBITO SUPERMERCADO EXTRA;-150.00
        2026-06-05;PIX RECEBIDO SALARIO;5000.00
      CSV
    end

    it "imports every row without requiring manual reformatting" do
      result = run(alt_csv_content)
      expect(result.imported).to eq(2)
      expect(result.errors).to eq([])
    end

    it "parses the ISO date and semicolon-separated amount correctly" do
      run(alt_csv_content)
      tx = user.transactions.find_by(description: "COMPRA DEBITO SUPERMERCADO EXTRA")
      expect(tx.occurred_on).to eq(Date.new(2026, 6, 1))
      expect(tx.amount).to eq(150.00)
      expect(tx.transaction_type).to eq("debit")
    end
  end

  it "collects a per-row error instead of raising when the value column has no parseable number" do
    content = <<~CSV
      Data,Descrição,Valor
      01/06/2026,LINHA SEM VALOR NUMERICO,R$
    CSV

    result = run(content)

    expect(result.imported).to eq(0)
    expect(result.errors.first).to match(/Valor inválido/)
  end

  it "returns a clear error when no known date/description/value columns are found" do
    content = <<~CSV
      Foo,Bar,Baz
      1,2,3
    CSV
    result = run(content)
    expect(result.imported).to eq(0)
    expect(result.errors.first).to match(/colunas reconhecidas/)
  end

  describe "SEC-22: CSV Formula Injection protection" do
    it "prefixa com apostrofe a descricao que comeca com =" do
      content = <<~CSV
        Data,Descrição,Valor
        01/06/2026,=2+2,-10.00
      CSV
      run(content)
      tx = user.transactions.find_by(amount: 10.00)
      expect(tx.description).to eq("'=2+2")
    end

    it "prefixa com apostrofe a descricao que comeca com +" do
      content = <<~CSV
        Data,Descrição,Valor
        01/06/2026,+SUM(A1,25.99
      CSV
      run(content)
      tx = user.transactions.find_by(amount: 25.99)
      expect(tx.description).to eq("'+SUM(A1")
    end

    it "prefixa com apostrofe a descricao que comeca com -" do
      content = <<~CSV
        Data,Descrição,Valor
        01/06/2026,-cmd|calc.exe!A1,30.00
      CSV
      run(content)
      tx = user.transactions.find_by(amount: 30.00)
      expect(tx.description).to eq("'-cmd|calc.exe!A1")
    end

    it "prefixa com apostrofe a descricao que comeca com @" do
      content = <<~CSV
        Data,Descrição,Valor
        01/06/2026,@SUM(A1:A10),-10.00
      CSV
      run(content)
      tx = user.transactions.find_by(amount: 10.00)
      expect(tx.description).to eq("'@SUM(A1:A10)")
    end

    it "nao altera descricao normal sem caractere-gatilho" do
      content = <<~CSV
        Data,Descrição,Valor
        01/06/2026,COMPRA NORMAL,-10.00
      CSV
      run(content)
      tx = user.transactions.find_by(amount: 10.00)
      expect(tx.description).to eq("COMPRA NORMAL")
    end
  end
end
