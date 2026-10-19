require "rails_helper"

RSpec.describe BankImport::ExternalIdBackfill, type: :service do
  let(:user) { create(:user) }
  let(:account) { create(:account, user: user) }

  it "uses the lowest free ordinal even when existing ids are out of order" do
    row = { occurred_on: Date.new(2026, 10, 10), description: "CAFÉ X", amount: BigDecimal("-5.00") }
    existing_ordinal_two = BankImport::ExternalId.for_row(row, account_key: account.id.to_s, ordinal: 2)
    existing_ordinal_four = BankImport::ExternalId.for_row(row, account_key: account.id.to_s, ordinal: 4)
    create(:transaction, user: user, account: account, description: "CAFÉ X", amount: 5, transaction_type: "debit",
      occurred_on: row[:occurred_on], external_id: existing_ordinal_two)
    create(:transaction, user: user, account: account, description: "CAFE X", amount: 5, transaction_type: "debit",
      occurred_on: row[:occurred_on], external_id: existing_ordinal_four)
    first_missing = create(:transaction, user: user, account: account, description: "CAFE X", amount: 5,
      transaction_type: "debit", occurred_on: row[:occurred_on])
    second_missing = create(:transaction, user: user, account: account, description: "CAFÉ X", amount: 5,
      transaction_type: "debit", occurred_on: row[:occurred_on])

    described_class.new(account).call

    expect(first_missing.reload.external_id).to eq(
      BankImport::ExternalId.for_row(row, account_key: account.id.to_s, ordinal: 1)
    )
    expect(second_missing.reload.external_id).to eq(
      BankImport::ExternalId.for_row(row, account_key: account.id.to_s, ordinal: 3)
    )
  end
end
