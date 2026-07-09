module BankImport
  class TransactionWriter
    DUPLICATE = :duplicate

    def initialize(user, account_id: nil)
      @user = user
      @account_id = account_id
    end

    def write!(description:, amount:, occurred_on:, installment_number: nil, installment_total: nil, notes: nil, member_id: nil)
      tx_type = amount >= 0 ? "credit" : "debit"
      hash = BankImport::DedupeHash.call(
        user_id: @user.id,
        account_id: @account_id,
        occurred_on: occurred_on,
        description: description,
        amount: amount,
        transaction_type: tx_type
      )

      return DUPLICATE if @user.transactions.exists?(dedupe_hash: hash)

      category = AutoCategorizerService.call(description, @user)

      @user.transactions.create!(
        description: description,
        amount: amount.abs,
        transaction_type: tx_type,
        occurred_on: occurred_on,
        category: category,
        account_id: @account_id,
        installment_number: installment_number,
        installment_total: installment_total,
        notes: notes,
        member_id: member_id,
        dedupe_hash: hash
      )
    end
  end
end
