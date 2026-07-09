class AddReimbursedByCategoryToCategories < ActiveRecord::Migration[8.1]
  def change
    add_reference :categories, :reimbursed_by_category,
      null: true, foreign_key: { to_table: :categories }, index: true
  end
end
