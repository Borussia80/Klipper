class CreateBudgets < ActiveRecord::Migration[8.1]
  def change
    create_table :budgets do |t|
      t.references :user,     null: false, foreign_key: true
      t.references :category, null: false, foreign_key: true
      t.decimal :amount_limit, precision: 15, scale: 2, null: false
      t.integer :period_month, null: false
      t.integer :period_year,  null: false
      t.timestamps
    end
    add_index :budgets, [ :user_id, :period_year, :period_month ]
    add_index :budgets, [ :user_id, :category_id, :period_year, :period_month ],
      unique: true, name: "index_budgets_on_user_category_period"
  end
end
