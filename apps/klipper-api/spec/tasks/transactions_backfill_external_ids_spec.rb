require "rails_helper"
require "rake"

# D5 (spec 06, I-1 a I-3a): preenche external_id dos lançamentos legados por
# conta. DRY_RUN apenas relata; a gravação exige rodar a task sem ele.
RSpec.describe "transactions:backfill_external_ids", type: :task do
  before(:all) do
    Rake.application.rake_require("tasks/transactions") unless Rake::Task.task_defined?("transactions:backfill_external_ids")
    Rake::Task.define_task(:environment)
  end

  let(:user) { create(:user) }
  let(:account) { create(:account, user: user) }
  let!(:first_coffee) do
    create(:transaction, user: user, account: account, description: "CAFÉ X", amount: 5,
      transaction_type: "debit", occurred_on: Date.new(2026, 10, 10))
  end
  let!(:second_coffee) do
    create(:transaction, user: user, account: account, description: "CAFE X", amount: 5,
      transaction_type: "debit", occurred_on: Date.new(2026, 10, 10))
  end
  let!(:without_account) do
    create(:transaction, user: user, account: nil, description: "Sem conta", amount: 10,
      occurred_on: Date.new(2026, 10, 11))
  end

  let(:task) { Rake::Task["transactions:backfill_external_ids"] }

  before { task.reenable }

  def run_task(env = {})
    original = $stdout
    $stdout = StringIO.new
    env.each { |key, value| ENV[key] = value }
    task.invoke
    $stdout.string
  ensure
    env.each_key { |key| ENV.delete(key) }
    $stdout = original
  end

  it "com DRY_RUN relata e não grava nada" do
    out = run_task("DRY_RUN" => "1")

    expect(out).to include("DRY RUN")
    expect(first_coffee.reload.external_id).to be_nil
    expect(second_coffee.reload.external_id).to be_nil
  end

  it "grava ids, inclusive distintos para lançamentos idênticos" do
    run_task

    expect(first_coffee.reload.external_id).to be_present
    expect(second_coffee.reload.external_id).to be_present
    expect(first_coffee.external_id).not_to eq(second_coffee.external_id)
  end

  it "deixa sem external_id o lançamento sem conta" do
    run_task

    expect(without_account.reload.external_id).to be_nil
  end

  it "é idempotente" do
    run_task

    expect { run_task }.not_to(change { Transaction.order(:id).pluck(:external_id) })
  end
end
