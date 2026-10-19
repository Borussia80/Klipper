module BankImport
  class TransactionWriter
    DUPLICATE = :duplicate

    def initialize(user, account_id: nil, ordinals: Hash.new(0))
      @user = user
      @account_id = account_id
      @ordinals = ordinals
    end

    def write!(description:, amount:, occurred_on:, installment_number: nil, installment_total: nil, notes: nil, member_id: nil)
      raise ActiveRecord::RecordNotFound, "Conta inválida" if @account_id.present? && !@user.accounts.exists?(id: @account_id)
      raise ActiveRecord::RecordNotFound, "Portador inválido" if member_id.present? && !@user.members.exists?(id: member_id)

      tx_type = amount >= 0 ? "credit" : "debit"
      hash = BankImport::DedupeHash.call(
        user_id: @user.id,
        account_id: @account_id,
        occurred_on: occurred_on,
        description: description,
        amount: amount,
        transaction_type: tx_type
      )

      external_id = external_id_for(description:, amount:, occurred_on:)
      return DUPLICATE if external_id && @user.transactions.where(account_id: @account_id).exists?(external_id:)
      return DUPLICATE if @user.transactions.where(dedupe_hash: hash, external_id: nil).exists?

      kind = BankImport::KindDetector.call(description: description, amount: amount)
      # Pagamento de fatura não é gasto nem renda: sem categoria, para não cair
      # em nenhum orçamento (spec 03, L-5).
      category = kind == "card_payment" ? nil : AutoCategorizerService.call(description, @user)

      @user.transactions.create!(
        description: description,
        amount: amount.abs,
        transaction_type: tx_type,
        kind: kind,
        occurred_on: occurred_on,
        category: category,
        account_id: @account_id,
        installment_number: installment_number,
        installment_total: installment_total,
        notes: notes,
        member_id: member_id,
        dedupe_hash: hash,
        external_id: external_id
      )
    rescue ActiveRecord::RecordNotUnique
      DUPLICATE
    end

    private

    def external_id_for(description:, amount:, occurred_on:)
      return nil if @account_id.blank?

      row = { description:, amount:, occurred_on: }
      identity = BankImport::ExternalId.for_row(row, account_key: @account_id.to_s, ordinal: 0)
      ordinal = @ordinals[identity] += 1
      BankImport::ExternalId.for_row(row, account_key: @account_id.to_s, ordinal:)
    end
  end
end
