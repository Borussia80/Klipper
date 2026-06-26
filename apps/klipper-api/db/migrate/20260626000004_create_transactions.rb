class CreateTransactions < ActiveRecord::Migration[8.1]
  def change
    create_table :transactions do |t|
      t.references :user,     null: false, foreign_key: true
      t.references :account,  null: false, foreign_key: true
      t.references :category, null: true,  foreign_key: true
      t.string  :description, null: false
      t.decimal :amount, precision: 15, scale: 2, null: false
      t.string  :transaction_type, null: false, default: "debit"
      t.date    :occurred_on, null: false
      t.text    :notes
      t.integer :installment_total
      t.integer :installment_number
      t.bigint  :parent_transaction_id
      t.timestamps
    end
    add_index :transactions, [ :user_id, :occurred_on ]
    add_index :transactions, [ :account_id, :occurred_on ]
    add_index :transactions, :parent_transaction_id
    add_foreign_key :transactions, :transactions, column: :parent_transaction_id
  end
end
