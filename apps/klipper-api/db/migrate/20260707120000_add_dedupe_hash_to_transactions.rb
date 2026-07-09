class AddDedupeHashToTransactions < ActiveRecord::Migration[8.1]
  disable_ddl_transaction!

  class TransactionForBackfill < ActiveRecord::Base
    self.table_name = "transactions"
  end

  def up
    add_column :transactions, :dedupe_hash, :string
    add_index :transactions, [ :user_id, :dedupe_hash ],
      name: "index_transactions_on_user_id_and_dedupe_hash"

    backfill_dedupe_hash!
  end

  def down
    remove_index :transactions, name: "index_transactions_on_user_id_and_dedupe_hash"
    remove_column :transactions, :dedupe_hash
  end

  private

  def backfill_dedupe_hash!
    TransactionForBackfill.reset_column_information

    say_with_time "Backfilling transactions.dedupe_hash" do
      TransactionForBackfill.unscoped.in_batches(of: 1000) do |batch|
        batch.each do |tx|
          TransactionForBackfill.unscoped.where(id: tx.id)
            .update_all(dedupe_hash: compute_dedupe_hash(tx))
        end
      end
    end
  end

  def compute_dedupe_hash(tx)
    parts = [
      tx.user_id,
      tx.account_id,
      tx.occurred_on.iso8601,
      tx.description.to_s.strip.downcase,
      BigDecimal(tx.amount.to_s).abs.round(2).to_s("F"),
      tx.transaction_type
    ]
    Digest::SHA256.hexdigest(parts.join("|"))
  end
end
