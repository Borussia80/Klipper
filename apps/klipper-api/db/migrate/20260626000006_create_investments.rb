class CreateInvestments < ActiveRecord::Migration[8.1]
  def change
    create_table :investments do |t|
      t.references :user,    null: false, foreign_key: true
      t.references :account, null: true,  foreign_key: true
      t.string  :ticker
      t.string  :name, null: false
      t.string  :investment_type, null: false, default: "stock"
      t.decimal :quantity,      precision: 15, scale: 6, null: false, default: 0
      t.decimal :average_price, precision: 15, scale: 4, null: false, default: 0
      t.string  :currency, null: false, default: "BRL"
      t.timestamps
    end
    add_index :investments, [ :user_id, :ticker ]
  end
end
