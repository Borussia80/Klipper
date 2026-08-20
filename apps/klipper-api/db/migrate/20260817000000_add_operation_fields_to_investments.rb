class AddOperationFieldsToInvestments < ActiveRecord::Migration[8.0]
  def up
    add_column :investments, :operation_type, :string, null: false, default: "buy"
    add_column :investments, :occurred_on, :date

    execute "UPDATE investments SET occurred_on = created_at::date WHERE occurred_on IS NULL"

    change_column_null :investments, :occurred_on, false
  end

  def down
    remove_column :investments, :occurred_on
    remove_column :investments, :operation_type
  end
end
