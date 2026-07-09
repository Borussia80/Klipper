class CreateMembers < ActiveRecord::Migration[8.1]
  def change
    create_table :members do |t|
      t.references :user, null: false, foreign_key: true
      t.string :name, null: false
      t.string :relationship, null: false, default: "titular"
      t.boolean :active, null: false, default: true
      t.timestamps
    end
    add_index :members, [ :user_id, :active ]
  end
end
