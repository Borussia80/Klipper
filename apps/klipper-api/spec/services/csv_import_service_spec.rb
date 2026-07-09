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

  it "only counts as duplicate the rows that match an existing transaction, importing the rest" do
    run(csv_content)
    extra_content = csv_content + "15/06/2026,COMPRA NOVA LOJA,-30.00\n"

    result = run(extra_content)

    expect(result.imported).to eq(1)
    expect(result.duplicates).to eq(3)
  end
end
