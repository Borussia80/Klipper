require "rails_helper"
require "rake"

RSpec.describe "accounts:audit_opening_balances", type: :task do
  before(:all) do
    Rake.application.rake_require("tasks/accounts") unless Rake::Task.task_defined?("accounts:audit_opening_balances")
    Rake::Task.define_task(:environment)
  end

  it "reports the old and corrected balance without changing any data" do
    account = create(:account, opening_balance: 500, opening_balance_on: Date.new(2026, 10, 10))
    create(:transaction, user: account.user, account: account, amount: 90, occurred_on: Date.new(2026, 10, 9))
    create(:transaction, user: account.user, account: account, amount: 20, occurred_on: Date.new(2026, 10, 10))
    task = Rake::Task["accounts:audit_opening_balances"]
    task.reenable
    before = [ account.attributes, account.transactions.map(&:attributes) ]

    expect { task.invoke }.to output(/account_id=#{account.id}.*legacy=390.00.*corrected=480.00/).to_stdout
    expect([ account.reload.attributes, account.transactions.reload.map(&:attributes) ]).to eq(before)
  end
end
