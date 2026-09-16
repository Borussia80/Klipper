require "rails_helper"
require "rake"

RSpec.describe "net_worth:backfill", type: :task do
  before(:all) do
    Rake.application.rake_require("tasks/net_worth") unless Rake::Task.task_defined?("net_worth:backfill")
    Rake::Task.define_task(:environment)
  end

  let(:task) { Rake::Task["net_worth:backfill"] }

  before { task.reenable }

  def run_task
    # A task escreve o relatório em stdout; nos testes só interessa o efeito.
    original = $stdout
    $stdout = StringIO.new
    task.invoke
    $stdout.string
  ensure
    $stdout = original
  end

  # O snapshot de setembro é recalculado com as operações que já existiam até o
  # fim daquele mês — a data de corte é occurred_on, não "agora".
  def snapshot_for(user, date)
    user.net_worth_snapshots.find_by(year: date.year, month: date.month)
  end

  context "for a user whose history has a sell" do
    let(:user) { create(:user) }
    let(:month) { Date.new(2026, 5, 31) }

    before do
      create(:account, user: user, balance: 1000)
      create(:investment, user: user, ticker: "IVVB11", quantity: 10, average_price: 100,
        occurred_on: Date.new(2026, 5, 10))
      create(:investment, :sell, user: user, ticker: "IVVB11", quantity: 4, average_price: 120,
        occurred_on: Date.new(2026, 5, 20))

      # Valor gravado pelo código defeituoso: a venda entrou somando (1000 + 480).
      create(:net_worth_snapshot, user: user, year: month.year, month: month.month,
        accounts_total: 1000, investments_cost: 1480, net_worth: 2480)
    end

    it "rewrites investments_cost with the sell subtracted" do
      run_task
      expect(snapshot_for(user, month).investments_cost.to_f).to eq(520.0)
    end

    it "rewrites net_worth from the corrected cost" do
      run_task
      expect(snapshot_for(user, month).net_worth.to_f).to eq(1520.0)
    end

    it "leaves accounts_total untouched, since the defect never affected it" do
      expect { run_task }.not_to change { snapshot_for(user, month).accounts_total }
    end

    it "is idempotent" do
      run_task
      task.reenable
      expect { run_task }.not_to change { snapshot_for(user, month).reload.net_worth }
    end

    it "records an auditable entry for the correction" do
      expect { run_task }.to change { user.audit_logs.where(event_type: "BACKFILL_NET_WORTH").count }.by(1)

      log = user.audit_logs.find_by(event_type: "BACKFILL_NET_WORTH")
      expect(log.status).to eq("success")
      expect(log.record_count).to eq(1)
      expect(log.metadata["corrections"].first).to include(
        "year" => 2026, "month" => 5, "net_worth_before" => "2480.0", "net_worth_after" => "1520.0"
      )
    end
  end

  context "for a user whose history has only buys" do
    let(:user) { create(:user) }
    let(:month) { Date.new(2026, 5, 31) }

    before do
      create(:account, user: user, balance: 1000)
      create(:investment, user: user, ticker: "PETR4", quantity: 10, average_price: 100,
        occurred_on: Date.new(2026, 5, 10))
      create(:net_worth_snapshot, user: user, year: month.year, month: month.month,
        accounts_total: 1000, investments_cost: 1000, net_worth: 2000)
    end

    it "leaves the snapshot alone" do
      expect { run_task }.not_to change { snapshot_for(user, month).reload.attributes.slice("investments_cost", "net_worth") }
    end

    it "does not record an audit entry when nothing changed" do
      expect { run_task }.not_to change { user.audit_logs.count }
    end
  end

  context "when a snapshot predates the operations" do
    let(:user) { create(:user) }

    before do
      create(:investment, user: user, ticker: "VALE3", quantity: 5, average_price: 50,
        occurred_on: Date.new(2026, 6, 1))
      create(:investment, :sell, user: user, ticker: "VALE3", quantity: 1, average_price: 50,
        occurred_on: Date.new(2026, 7, 1))
      create(:net_worth_snapshot, user: user, year: 2026, month: 5,
        accounts_total: 0, investments_cost: 0, net_worth: 0)
    end

    it "does not pull later operations into an earlier month" do
      run_task
      snapshot = user.net_worth_snapshots.find_by(year: 2026, month: 5)
      expect(snapshot.investments_cost.to_f).to eq(0.0)
    end
  end

  context "in dry run" do
    let(:user) { create(:user) }

    before do
      create(:investment, user: user, ticker: "IVVB11", quantity: 10, average_price: 100,
        occurred_on: Date.new(2026, 5, 10))
      create(:investment, :sell, user: user, ticker: "IVVB11", quantity: 4, average_price: 120,
        occurred_on: Date.new(2026, 5, 20))
      create(:net_worth_snapshot, user: user, year: 2026, month: 5,
        accounts_total: 0, investments_cost: 1480, net_worth: 1480)
      ENV["DRY_RUN"] = "1"
    end

    after { ENV.delete("DRY_RUN") }

    it "reports what would change without writing" do
      output = run_task
      expect(output).to include("1480.0", "520.0")
      expect(user.net_worth_snapshots.find_by(year: 2026, month: 5).investments_cost.to_f).to eq(1480.0)
    end

    it "does not record an audit entry" do
      expect { run_task }.not_to change { AuditLog.count }
    end
  end
end
