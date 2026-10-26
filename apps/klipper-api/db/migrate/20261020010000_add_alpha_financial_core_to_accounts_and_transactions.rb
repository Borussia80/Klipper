class AddAlphaFinancialCoreToAccountsAndTransactions < ActiveRecord::Migration[8.1]
  def up
    add_column :accounts, :opening_balance, :decimal, precision: 15, scale: 2, default: 0, null: false
    add_column :accounts, :opening_balance_on, :date
    execute <<~SQL.squish
      UPDATE accounts
      SET opening_balance = balance,
          opening_balance_on = created_at::date
      WHERE opening_balance_on IS NULL
    SQL
    change_column_null :accounts, :opening_balance_on, false

    add_column :transactions, :deleted_at, :datetime
    add_column :transactions, :transfer_pair_id, :string
    add_index :transactions, :deleted_at
    add_index :transactions, :transfer_pair_id
  end

  def down
    remove_index :transactions, :transfer_pair_id
    remove_index :transactions, :deleted_at
    remove_column :transactions, :transfer_pair_id
    remove_column :transactions, :deleted_at
    remove_column :accounts, :opening_balance_on
    remove_column :accounts, :opening_balance
  end
end
