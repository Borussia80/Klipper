require "rails_helper"

RSpec.describe BankImport::ExternalId, type: :service do
  def rows
    [
      { occurred_on: Date.new(2026, 10, 10), description: "CAFÉ X", amount: BigDecimal("-5.00") },
      { occurred_on: Date.new(2026, 10, 10), description: "CAFE X", amount: BigDecimal("5.00") },
      { occurred_on: Date.new(2026, 10, 11), description: "Mercado", amount: BigDecimal("-42.50") }
    ]
  end

  def external_ids(import_rows, account_key: "account-a")
    described_class.for_rows(import_rows, account_key:).pluck(:external_id)
  end

  it "assigns distinct, sequential ordinals to identical coffees" do
    result = described_class.for_rows([ rows.first, rows.first ], account_key: "account-a")
    ids = result.pluck(:external_id)

    expect(ids).to eq([
      Digest::SHA256.hexdigest("account-a|2026-10-10|cafe x|-5.00|1"),
      Digest::SHA256.hexdigest("account-a|2026-10-10|cafe x|-5.00|2")
    ])
  end

  it "builds an id for an explicit row ordinal" do
    row = rows.first

    expect(described_class.for_row(row, account_key: "account-a", ordinal: 2)).to eq(
      Digest::SHA256.hexdigest("account-a|2026-10-10|cafe x|-5.00|2")
    )
  end

  it "keeps a debit and a credit of the same amount distinct" do
    debit, credit = rows.first(2)

    expect(external_ids([ debit ])).not_to eq(external_ids([ credit ]))
  end

  it "is stable when rows are reordered" do
    expect(external_ids(rows.reverse)).to contain_exactly(*external_ids(rows))
  end

  it "is stable when a file is divided into files containing different identities" do
    full_file_ids = external_ids(rows.values_at(0, 2))
    split_file_ids = external_ids([ rows[0] ]) + external_ids([ rows[2] ])

    expect(split_file_ids).to contain_exactly(*full_file_ids)
  end

  it "does not depend on a filename supplied as extra row metadata" do
    original_name = rows.map { |row| row.merge(filename: "fatura-outubro.pdf") }
    renamed_file = rows.map { |row| row.merge(filename: "extrato.pdf") }

    expect(external_ids(original_name)).to eq(external_ids(renamed_file))
  end

  it "is stable when the same content is reimported" do
    expect(external_ids(rows)).to eq(external_ids(rows))
  end

  it "changes when the account changes" do
    expect(external_ids(rows, account_key: "account-a")).not_to eq(external_ids(rows, account_key: "account-b"))
  end
end
