class AddExternalIdToTransactions < ActiveRecord::Migration[8.1]
  def change
    add_column :transactions, :external_id, :string
    add_index :transactions, [ :account_id, :external_id ], unique: true,
      where: "external_id IS NOT NULL", name: "index_transactions_on_account_id_and_external_id"
  end
end
