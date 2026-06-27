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

ActiveRecord::Schema[8.1].define(version: 2026_06_27_024311) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"

  create_table "accounts", force: :cascade do |t|
    t.string "account_type", default: "checking", null: false
    t.boolean "active", default: true, null: false
    t.decimal "balance", precision: 15, scale: 2, default: "0.0", null: false
    t.datetime "created_at", null: false
    t.string "currency", default: "BRL", null: false
    t.string "institution"
    t.string "name", null: false
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["user_id", "active"], name: "index_accounts_on_user_id_and_active"
    t.index ["user_id"], name: "index_accounts_on_user_id"
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
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["user_id", "category_type"], name: "index_categories_on_user_id_and_category_type"
    t.index ["user_id"], name: "index_categories_on_user_id"
  end

  create_table "investments", force: :cascade do |t|
    t.bigint "account_id"
    t.decimal "average_price", precision: 15, scale: 4, default: "0.0", null: false
    t.datetime "created_at", null: false
    t.string "currency", default: "BRL", null: false
    t.string "investment_type", default: "stock", null: false
    t.string "name", null: false
    t.decimal "quantity", precision: 15, scale: 6, default: "0.0", null: false
    t.string "ticker"
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["account_id"], name: "index_investments_on_account_id"
    t.index ["user_id", "ticker"], name: "index_investments_on_user_id_and_ticker"
    t.index ["user_id"], name: "index_investments_on_user_id"
  end

  create_table "transactions", force: :cascade do |t|
    t.bigint "account_id"
    t.decimal "amount", precision: 15, scale: 2, null: false
    t.bigint "category_id"
    t.datetime "created_at", null: false
    t.string "description", null: false
    t.integer "installment_number"
    t.integer "installment_total"
    t.text "notes"
    t.date "occurred_on", null: false
    t.bigint "parent_transaction_id"
    t.string "transaction_type", default: "debit", null: false
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["account_id", "occurred_on"], name: "index_transactions_on_account_id_and_occurred_on"
    t.index ["account_id"], name: "index_transactions_on_account_id"
    t.index ["category_id"], name: "index_transactions_on_category_id"
    t.index ["parent_transaction_id"], name: "index_transactions_on_parent_transaction_id"
    t.index ["user_id", "occurred_on"], name: "index_transactions_on_user_id_and_occurred_on"
    t.index ["user_id"], name: "index_transactions_on_user_id"
  end

  create_table "users", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "email", null: false
    t.string "name"
    t.string "password_digest", null: false
    t.datetime "updated_at", null: false
    t.index ["email"], name: "index_users_on_email", unique: true
  end

  add_foreign_key "accounts", "users"
  add_foreign_key "budgets", "categories"
  add_foreign_key "budgets", "users"
  add_foreign_key "categories", "users"
  add_foreign_key "investments", "accounts"
  add_foreign_key "investments", "users"
  add_foreign_key "transactions", "accounts"
  add_foreign_key "transactions", "categories"
  add_foreign_key "transactions", "transactions", column: "parent_transaction_id"
  add_foreign_key "transactions", "users"
end
