module SignedImportRow
  def signed_row(occurred_on:, description:, amount:, installment_number: nil, installment_total: nil, **extra)
    canonical = {
      occurred_on: occurred_on,
      description: description,
      amount: amount,
      installment_number: installment_number,
      installment_total: installment_total
    }

    canonical.stringify_keys.merge("token" => BankImport::RowSigner.sign(canonical)).merge(extra.stringify_keys)
  end
end

RSpec.configure { |config| config.include SignedImportRow }
