require "rails_helper"

RSpec.describe BankImport::AmountParser, type: :service do
  it "parses a plain ASCII-negative decimal (existing CSV format)" do
    expect(described_class.call("-150.00")).to eq(BigDecimal("-150.00"))
  end

  it "parses a plain positive decimal (existing CSV format)" do
    expect(described_class.call("5000.00")).to eq(BigDecimal("5000.00"))
  end

  it "parses Brazilian comma-decimal without thousands separator" do
    expect(described_class.call("150,00")).to eq(BigDecimal("150.00"))
  end

  it "parses Brazilian comma-decimal with thousands separator and leading minus" do
    expect(described_class.call("-1.234,56")).to eq(BigDecimal("-1234.56"))
  end

  it "parses small decimal values" do
    expect(described_class.call("0,02")).to eq(BigDecimal("0.02"))
  end

  it "parses large values with multiple thousands separators" do
    expect(described_class.call("1.234.567,89")).to eq(BigDecimal("1234567.89"))
  end

  it "normalizes a Unicode minus sign (Nubank-style) to ASCII" do
    expect(described_class.call("−R$ 160,00")).to eq(BigDecimal("-160.00"))
  end

  it "strips currency symbols and whitespace" do
    expect(described_class.call("R$ 9.603,90")).to eq(BigDecimal("9603.90"))
  end

  it "returns nil for blank input" do
    expect(described_class.call("")).to be_nil
    expect(described_class.call(nil)).to be_nil
  end
end
