require "rails_helper"

RSpec.describe BankImport::OwnTransferMatcher do
  Identity = Struct.new(:names, :cpf_mask)

  let(:identity) { Identity.new([ "Jose Teste Da Silva" ], "123.456") }
  let(:date) { Date.new(2026, 10, 1) }

  def row(account_key:, amount:, description:, occurred_on: date)
    {
      account_key:,
      occurred_on:,
      description:,
      amount: BigDecimal(amount.to_s)
    }
  end

  def match(rows)
    described_class.call(rows, identity:)
  end

  it "pairs own PIX transfers between distinct accounts on the same day" do
    rows = [
      row(account_key: "itau", amount: -500, description: "PIX TRANSF Jose Teste Da Silva"),
      row(account_key: "nubank", amount: 500,
          description: "Transferencia recebida pelo Pix Jose Teste Da Silva 123.456")
    ]

    expect(match(rows)).to equal(rows)
    expect(rows.map { |item| item[:own_transfer] }).to eq([
      { state: :paired, pair_index: 1 },
      { state: :paired, pair_index: 0 }
    ])
  end

  it "marks a strong candidate with no imported counterpart as to link" do
    rows = [ row(account_key: "itau", amount: -500, description: "PIX TRANSF Jose Teste Da Silva") ]

    expect(match(rows).first[:own_transfer]).to eq({ state: :to_link, pair_index: nil })
  end

  it "does not treat the holder name alone as an own transfer" do
    rows = [ row(account_key: "itau", amount: -500, description: "Pagamento para Jose Teste Da Silva") ]

    expect(match(rows).first[:own_transfer]).to be_nil
  end

  it "does not accept a masked CPF belonging to someone else" do
    rows = [ row(account_key: "itau", amount: -500,
                 description: "Pagamento para Jose Teste Da Silva 987.654") ]

    expect(match(rows).first[:own_transfer]).to be_nil
  end

  it "leaves all candidates to link when the amount has two possible counterparts" do
    rows = [
      row(account_key: "itau", amount: -500, description: "PIX TRANSF Jose Teste Da Silva"),
      row(account_key: "nubank", amount: 500, description: "PIX recebido Jose Teste Da Silva"),
      row(account_key: "banco_generico", amount: 500,
          description: "Transferencia recebida Jose Teste Da Silva")
    ]

    expect(match(rows).map { |item| item[:own_transfer] }).to eq([
      { state: :to_link, pair_index: nil },
      { state: :to_link, pair_index: nil },
      { state: :to_link, pair_index: nil }
    ])
  end

  it "requires a counterpart for a truncated holder-name prefix" do
    rows = [ row(account_key: "itau", amount: -500, description: "Pix enviado Jose Teste Da Si") ]

    expect(match(rows).first[:own_transfer]).to be_nil
  end

  it "pairs a truncated holder-name prefix when a counterpart exists" do
    rows = [
      row(account_key: "itau", amount: -500, description: "Pix enviado Jose Teste Da Si"),
      row(account_key: "nubank", amount: 500,
          description: "Transferencia recebida Jose Teste Da Silva 123.456")
    ]

    expect(match(rows).map { |item| item[:own_transfer] }).to eq([
      { state: :paired, pair_index: 1 },
      { state: :paired, pair_index: 0 }
    ])
  end

  it "marks RDB application and redemption as investment transfers" do
    rows = [
      row(account_key: "nubank", amount: -500.91, description: "Aplicacao RDB"),
      row(account_key: "nubank", amount: 500.91, description: "Resgate RDB")
    ]

    expect(match(rows).map { |item| item[:own_transfer] }).to eq([
      { state: :investment, pair_index: nil },
      { state: :investment, pair_index: nil }
    ])
  end

  it "keeps Nu Pagamentos boleto payments regular" do
    rows = [ row(account_key: "nubank", amount: -350,
                 description: "Pagamento de boleto efetuado - NU PAGAMENTOS SA") ]

    expect(match(rows).first[:own_transfer]).to be_nil
  end

  it "never treats Pix devolvido as an own transfer" do
    rows = [ row(account_key: "itau", amount: 500,
                 description: "Pix devolvido Jose Teste Da Silva 123.456") ]

    expect(match(rows).first[:own_transfer]).to be_nil
  end

  it "pairs candidates up to three days apart, but not four days apart" do
    near_rows = [
      row(account_key: "itau", amount: -500, description: "PIX TRANSF Jose Teste Da Silva"),
      row(account_key: "nubank", amount: 500, occurred_on: date + 3,
          description: "PIX recebido Jose Teste Da Silva")
    ]
    far_rows = [
      row(account_key: "itau", amount: -500, description: "PIX TRANSF Jose Teste Da Silva"),
      row(account_key: "nubank", amount: 500, occurred_on: date + 4,
          description: "PIX recebido Jose Teste Da Silva")
    ]

    expect(match(near_rows).map { |item| item[:own_transfer][:state] }).to eq(%i[paired paired])
    expect(match(far_rows).map { |item| item[:own_transfer][:state] }).to eq(%i[to_link to_link])
  end

  it "does not pair candidates from the same account" do
    rows = [
      row(account_key: "itau", amount: -500, description: "PIX TRANSF Jose Teste Da Silva"),
      row(account_key: "itau", amount: 500, description: "PIX recebido Jose Teste Da Silva")
    ]

    expect(match(rows).map { |item| item[:own_transfer] }).to eq([
      { state: :to_link, pair_index: nil },
      { state: :to_link, pair_index: nil }
    ])
  end

  # Extrato que imprime só o primeiro nome colado à data ("PIX TRANSF JOSE01/10").
  describe "first-name-only label (weak candidate)" do
    let(:strong_nubank) do
      row(account_key: "nubank", amount: 500,
          description: "Transferencia recebida pelo Pix Jose Teste Da Silva 123.456")
    end

    it "pairs with a strong candidate of opposite sign" do
      rows = [ row(account_key: "itau", amount: -500, description: "PIX TRANSF JOSE01/10"), strong_nubank ]

      expect(match(rows).map { |item| item[:own_transfer] }).to eq([
        { state: :paired, pair_index: 1 },
        { state: :paired, pair_index: 0 }
      ])
    end

    it "stays unmarked without a counterpart" do
      rows = [ row(account_key: "itau", amount: -500, description: "PIX TRANSF JOSE01/10") ]

      expect(match(rows).first[:own_transfer]).to be_nil
    end

    it "never pairs with another weak candidate" do
      rows = [
        row(account_key: "itau", amount: -500, description: "PIX TRANSF JOSE01/10"),
        row(account_key: "nubank", amount: 500, description: "Pix recebido JOSE")
      ]

      expect(match(rows).map { |item| item[:own_transfer] }).to eq([ nil, nil ])
    end

    it "does not match a different name that merely starts with the first name" do
      rows = [ row(account_key: "itau", amount: -500, description: "PIX TRANSF JOSEFA01/10"), strong_nubank ]

      expect(match(rows).first[:own_transfer]).to be_nil
    end
  end
end
