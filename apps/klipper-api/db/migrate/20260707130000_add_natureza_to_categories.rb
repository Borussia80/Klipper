class AddNaturezaToCategories < ActiveRecord::Migration[8.1]
  def change
    add_column :categories, :natureza, :string, null: false, default: "variavel"
    add_index :categories, [ :user_id, :natureza ]
  end
end
