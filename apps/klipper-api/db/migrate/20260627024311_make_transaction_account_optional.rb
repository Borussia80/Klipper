class MakeTransactionAccountOptional < ActiveRecord::Migration[8.1]
  def change
    change_column_null :transactions, :account_id, true
  end
end
