require "rails_helper"

RSpec.describe BankImport::DescriptionNormalizer, type: :service do
  it "lowercases, removes accents, and collapses surrounding whitespace" do
    expect(described_class.call("  CAFÉ   São  João  ")).to eq("cafe sao joao")
  end

  it "removes only authorization numbers preceded by a recognized label" do
    text = "Compra NSU 123456 AUT: 98765 autorização 4455"

    expect(described_class.call(text)).to eq("compra")
  end

  it "preserves unrelated numbers that are part of the transaction identity" do
    text = "Parcela 03/12 cartao final 4321 valor 150,00"

    expect(described_class.call(text)).to eq("parcela 03/12 cartao final 4321 valor 150,00")
  end
end
