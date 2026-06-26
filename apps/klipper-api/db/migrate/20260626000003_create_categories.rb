class CreateCategories < ActiveRecord::Migration[8.1]
  def change
    create_table :categories do |t|
      t.references :user, null: false, foreign_key: true
      t.string :name, null: false
      t.string :icon, null: false, default: "wallet"
      t.string :category_type, null: false, default: "expense"
      t.string :color, default: "#6B93AE"
      t.boolean :active, null: false, default: true
      t.timestamps
    end
    add_index :categories, [ :user_id, :category_type ]
  end
end
