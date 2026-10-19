require "rails_helper"

RSpec.describe BankImport::PreviewSerializer do
  let(:user) { create(:user, own_names: [ "Jose Teste Da Silva" ], own_cpf_mask: "123.456") }
  let(:account) { create(:account, user: user) }

  def row(description:, amount:, occurred_on: Date.new(2026, 10, 1))
    CsvImportService::PreviewRow.new(
      occurred_on:, description:, amount: BigDecimal(amount.to_s), page: 2, metadata: {},
      installment_number: nil, installment_total: nil
    )
  end

  def serialize(rows)
    described_class.new(user, account_id: account.id).serialize(rows)
  end

  it "serializes an investment row (no pair index) without raising" do
    result = serialize([ row(description: "Aplicacao RDB", amount: -5000.91) ])

    expect(result.first[:own_transfer]).to eq({ state: "investment", counterpart: nil })
  end

  it "serializes a to-link row (strong candidate without pair) without raising" do
    result = serialize([
      row(description: "Transferencia recebida pelo Pix - Jose Teste Da Silva - 123.456", amount: 300)
    ])

    expect(result.first[:own_transfer]).to eq({ state: "to_link", counterpart: nil })
  end

  it "keeps own_transfer nil for rows without suggestion" do
    result = serialize([ row(description: "Pagamento de boleto efetuado - NU PAGAMENTOS SA", amount: -350) ])

    expect(result.first[:own_transfer]).to be_nil
  end
end
