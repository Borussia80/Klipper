require "set"

module BankImport
  class ExternalIdBackfill
    def initialize(account)
      @account = account
    end

    def call(dry_run: false)
      transactions = Transaction.where(account_id: @account.id)
      assigned_ids = transactions.where.not(external_id: nil).pluck(:external_id).to_set
      changes = transactions.where(external_id: nil).order(:id).filter_map do |transaction|
        external_id = next_free_external_id(transaction, assigned_ids)
        assigned_ids << external_id
        [ transaction, external_id ]
      end

      return changes if dry_run

      Transaction.transaction do
        # update_columns: só o identificador muda, e uma validação de lançamento
        # antigo (ex.: data futura) não pode derrubar o assign_account no meio.
        changes.each { |transaction, external_id| transaction.update_columns(external_id:) }
      end
      changes
    end

    private

    def next_free_external_id(transaction, assigned_ids)
      row = {
        occurred_on: transaction.occurred_on,
        description: transaction.description,
        amount: signed_amount(transaction)
      }
      ordinal = 1

      loop do
        external_id = ExternalId.for_row(row, account_key: @account.id.to_s, ordinal:)
        return external_id unless assigned_ids.include?(external_id)

        ordinal += 1
      end
    end

    def signed_amount(transaction)
      transaction.transaction_type == "debit" ? -transaction.amount : transaction.amount
    end
  end
end
