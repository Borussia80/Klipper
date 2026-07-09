module BankImport
  class DedupeHash
    def self.call(user_id:, account_id:, occurred_on:, description:, amount:, transaction_type:)
      parts = [
        user_id,
        account_id.presence&.to_s,
        occurred_on.to_date.iso8601,
        description.to_s.strip.downcase,
        BigDecimal(amount.to_s).abs.round(2).to_s("F"),
        transaction_type
      ]
      Digest::SHA256.hexdigest(parts.join("|"))
    end
  end
end
