require "rails_helper"

RSpec.describe BankImport::DedupeHash, type: :service do
  def call(**overrides)
    described_class.call(
      user_id: 1, account_id: 2, occurred_on: Date.new(2026, 6, 25),
      description: "Loja X", amount: BigDecimal("-10.00"), transaction_type: "debit",
      **overrides
    )
  end

  it "is deterministic for identical inputs" do
    expect(call).to eq(call)
  end

  it "ignores case and surrounding whitespace in description" do
    expect(call(description: "  loja x  ")).to eq(call(description: "Loja X"))
  end

  it "treats amount sign the same for equal absolute value" do
    expect(call(amount: BigDecimal("10.00"))).to eq(call(amount: BigDecimal("-10.00")))
  end

  it "differs when transaction_type differs" do
    expect(call(transaction_type: "credit")).not_to eq(call(transaction_type: "debit"))
  end

  it "differs when account_id differs" do
    expect(call(account_id: 3)).not_to eq(call(account_id: 2))
  end

  it "differs when user_id differs" do
    expect(call(user_id: 2)).not_to eq(call(user_id: 1))
  end

  it "treats nil and blank account_id the same" do
    expect(call(account_id: nil)).to eq(call(account_id: ""))
  end

  it "treats integer and string account_id the same" do
    expect(call(account_id: 2)).to eq(call(account_id: "2"))
  end
end
