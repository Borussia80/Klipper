require "digest"

module BankImport
  class ExternalId
    # Identical means same date, normalized description, and signed amount (a debit and a credit of the same value are different rows); indistinguishable rows get ordinals by occurrence.
    def self.for_rows(rows, account_key:)
      ordinals = Hash.new(0)

      rows.map do |row|
        identity = identity_for(row)
        ordinals[identity] += 1
        row.merge(external_id: for_row(row, account_key:, ordinal: ordinals[identity]))
      end
    end

    def self.for_row(row, account_key:, ordinal:)
      Digest::SHA256.hexdigest([ account_key, *identity_for(row), ordinal ].join("|"))
    end

    def self.identity_for(row)
      [
        row.fetch(:occurred_on).to_date.iso8601,
        DescriptionNormalizer.call(row.fetch(:description)),
        format("%.2f", BigDecimal(row.fetch(:amount).to_s).round(2))
      ]
    end
    private_class_method :identity_for
  end
end
