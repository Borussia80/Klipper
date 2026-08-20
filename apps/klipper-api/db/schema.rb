# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.1].define(version: 2026_08_20_000000) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"

  create_table "accounts", force: :cascade do |t|
    t.string "account_type", default: "checking", null: false
    t.boolean "active", default: true, null: false
    t.decimal "balance", precision: 15, scale: 2, default: "0.0", null: false
    t.datetime "created_at", null: false
    t.string "currency", default: "BRL", null: false
    t.string "institution"
    t.decimal "iof_projetado", precision: 15, scale: 2
    t.decimal "juros_rotativo_aa", precision: 7, scale: 3
    t.decimal "juros_rotativo_am", precision: 6, scale: 3
    t.string "name", null: false
    t.decimal "pagamento_minimo", precision: 15, scale: 2
    t.datetime "saldo_atualizado_em"
    t.decimal "saldo_fatura_atual", precision: 15, scale: 2
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["user_id", "active"], name: "index_accounts_on_user_id_and_active"
    t.index ["user_id"], name: "index_accounts_on_user_id"
  end

  create_table "audit_logs", force: :cascade do |t|
    t.string "checksum"
    t.datetime "created_at", null: false
    t.string "event_type", null: false
    t.jsonb "metadata", default: {}, null: false
    t.integer "record_count", default: 0, null: false
    t.string "status", default: "success", null: false
    t.bigint "user_id", null: false
    t.index ["created_at"], name: "index_audit_logs_on_created_at"
    t.index ["user_id", "event_type", "created_at"], name: "index_audit_logs_on_user_event_created"
    t.index ["user_id"], name: "index_audit_logs_on_user_id"
  end

  create_table "budgets", force: :cascade do |t|
    t.decimal "amount_limit", precision: 15, scale: 2, null: false
    t.bigint "category_id", null: false
    t.datetime "created_at", null: false
    t.integer "period_month", null: false
    t.integer "period_year", null: false
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["category_id"], name: "index_budgets_on_category_id"
    t.index ["user_id", "category_id", "period_year", "period_month"], name: "index_budgets_on_user_category_period", unique: true
    t.index ["user_id", "period_year", "period_month"], name: "index_budgets_on_user_id_and_period_year_and_period_month"
    t.index ["user_id"], name: "index_budgets_on_user_id"
  end

  create_table "categories", force: :cascade do |t|
    t.boolean "active", default: true, null: false
    t.string "category_type", default: "expense", null: false
    t.string "color", default: "#6B93AE"
    t.datetime "created_at", null: false
    t.string "icon", default: "wallet", null: false
    t.string "name", null: false
    t.string "natureza", default: "variavel", null: false
    t.bigint "reimbursed_by_category_id"
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["reimbursed_by_category_id"], name: "index_categories_on_reimbursed_by_category_id"
    t.index ["user_id", "category_type"], name: "index_categories_on_user_id_and_category_type"
    t.index ["user_id", "natureza"], name: "index_categories_on_user_id_and_natureza"
    t.index ["user_id"], name: "index_categories_on_user_id"
  end

  create_table "investments", force: :cascade do |t|
    t.bigint "account_id"
    t.decimal "average_price", precision: 15, scale: 4, default: "0.0", null: false
    t.datetime "created_at", null: false
    t.string "currency", default: "BRL", null: false
    t.string "investment_type", default: "stock", null: false
    t.string "name", null: false
    t.date "occurred_on", null: false
    t.string "operation_type", default: "buy", null: false
    t.decimal "quantity", precision: 15, scale: 6, default: "0.0", null: false
    t.string "ticker"
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["account_id"], name: "index_investments_on_account_id"
    t.index ["user_id", "ticker"], name: "index_investments_on_user_id_and_ticker"
    t.index ["user_id"], name: "index_investments_on_user_id"
  end

  create_table "members", force: :cascade do |t|
    t.boolean "active", default: true, null: false
    t.datetime "created_at", null: false
    t.string "name", null: false
    t.string "relationship", default: "titular", null: false
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["user_id", "active"], name: "index_members_on_user_id_and_active"
    t.index ["user_id"], name: "index_members_on_user_id"
  end

  create_table "net_worth_snapshots", force: :cascade do |t|
    t.decimal "accounts_total", precision: 14, scale: 2, null: false
    t.datetime "created_at", null: false
    t.decimal "investments_cost", precision: 14, scale: 2, null: false
    t.integer "month", null: false
    t.decimal "net_worth", precision: 14, scale: 2, null: false
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.integer "year", null: false
    t.index ["user_id", "year", "month"], name: "index_net_worth_snapshots_on_user_id_and_year_and_month", unique: true
    t.index ["user_id"], name: "index_net_worth_snapshots_on_user_id"
  end

  create_table "solid_cache_entries", force: :cascade do |t|
    t.integer "byte_size", null: false
    t.datetime "created_at", null: false
    t.binary "key", null: false
    t.bigint "key_hash", null: false
    t.binary "value", null: false
    t.index ["byte_size"], name: "index_solid_cache_entries_on_byte_size"
    t.index ["key_hash", "byte_size"], name: "index_solid_cache_entries_on_key_hash_and_byte_size"
    t.index ["key_hash"], name: "index_solid_cache_entries_on_key_hash", unique: true
  end

  create_table "transactions", force: :cascade do |t|
    t.bigint "account_id"
    t.decimal "amount", precision: 15, scale: 2, null: false
    t.bigint "category_id"
    t.datetime "created_at", null: false
    t.string "dedupe_hash"
    t.string "description", null: false
    t.integer "installment_number"
    t.integer "installment_total"
    t.bigint "member_id"
    t.text "notes"
    t.date "occurred_on", null: false
    t.bigint "parent_transaction_id"
    t.string "transaction_type", default: "debit", null: false
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["account_id", "occurred_on"], name: "index_transactions_on_account_id_and_occurred_on"
    t.index ["account_id"], name: "index_transactions_on_account_id"
    t.index ["category_id"], name: "index_transactions_on_category_id"
    t.index ["member_id"], name: "index_transactions_on_member_id"
    t.index ["parent_transaction_id"], name: "index_transactions_on_parent_transaction_id"
    t.index ["user_id", "dedupe_hash"], name: "index_transactions_on_user_id_and_dedupe_hash"
    t.index ["user_id", "occurred_on"], name: "index_transactions_on_user_id_and_occurred_on"
    t.index ["user_id"], name: "index_transactions_on_user_id"
  end

  create_table "users", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "email", null: false
    t.string "name"
    t.string "password_digest", null: false
    t.integer "token_version", default: 1, null: false
    t.datetime "updated_at", null: false
    t.index ["email"], name: "index_users_on_email", unique: true
  end

  add_foreign_key "accounts", "users"
  add_foreign_key "audit_logs", "users"
  add_foreign_key "budgets", "categories"
  add_foreign_key "budgets", "users"
  add_foreign_key "categories", "categories", column: "reimbursed_by_category_id"
  add_foreign_key "categories", "users"
  add_foreign_key "investments", "accounts"
  add_foreign_key "investments", "users"
  add_foreign_key "members", "users"
  add_foreign_key "net_worth_snapshots", "users"
  add_foreign_key "transactions", "accounts"
  add_foreign_key "transactions", "categories"
  add_foreign_key "transactions", "members"
  add_foreign_key "transactions", "transactions", column: "parent_transaction_id"
  add_foreign_key "transactions", "users"
end
