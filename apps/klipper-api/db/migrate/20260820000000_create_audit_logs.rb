class CreateAuditLogs < ActiveRecord::Migration[8.1]
  def change
    create_table :audit_logs do |t|
      t.string     :event_type,   null: false
      t.string     :status,       null: false, default: "success"
      t.integer    :record_count, null: false, default: 0
      t.string     :checksum
      t.jsonb      :metadata,     null: false, default: {}
      t.references :user,         null: false, foreign_key: true

      t.datetime   :created_at,   null: false
    end

    add_index :audit_logs, [ :user_id, :event_type, :created_at ],
              name: "index_audit_logs_on_user_event_created"
    add_index :audit_logs, [ :created_at ], name: "index_audit_logs_on_created_at"
  end
end
