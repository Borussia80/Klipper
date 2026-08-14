class CreateNetWorthSnapshots < ActiveRecord::Migration[8.1]
  def change
    create_table :net_worth_snapshots do |t|
      t.references :user, null: false, foreign_key: true
      t.integer :year, null: false
      t.integer :month, null: false
      t.decimal :accounts_total, precision: 14, scale: 2, null: false
      t.decimal :investments_cost, precision: 14, scale: 2, null: false
      t.decimal :net_worth, precision: 14, scale: 2, null: false

      t.timestamps
    end

    add_index :net_worth_snapshots, [ :user_id, :year, :month ], unique: true
  end
end
