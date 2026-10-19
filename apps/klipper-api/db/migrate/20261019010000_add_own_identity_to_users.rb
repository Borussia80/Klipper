class AddOwnIdentityToUsers < ActiveRecord::Migration[8.1]
  def change
    add_column :users, :own_names, :text, array: true, default: [], null: false
    add_column :users, :own_cpf_mask, :string
  end
end
