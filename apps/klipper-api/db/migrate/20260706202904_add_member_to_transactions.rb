class AddMemberToTransactions < ActiveRecord::Migration[8.1]
  def change
    add_reference :transactions, :member, null: true, foreign_key: true
  end
end
