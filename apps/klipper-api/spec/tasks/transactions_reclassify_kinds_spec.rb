require "rails_helper"
require "rake"

# M2 (plano D1, Q6): reclassifica lançamentos já gravados com a mesma detecção da
# importação. DRY_RUN só relata; a gravação exige rodar sem ele.
RSpec.describe "transactions:reclassify_kinds", type: :task do
  before(:all) do
    Rake.application.rake_require("tasks/transactions") unless Rake::Task.task_defined?("transactions:reclassify_kinds")
    Rake::Task.define_task(:environment)
  end

  let(:task) { Rake::Task["transactions:reclassify_kinds"] }
  let(:user) { create(:user) }
  let(:renda) { create(:category, :income, user: user, name: "Renda") }
  let!(:boleto) do
    create(:transaction, user: user, description: "PAG BOLETO NU PAGAMENTOS SA", amount: 320,
      transaction_type: "debit", category: renda, occurred_on: Date.new(2026, 6, 5))
  end
  let!(:estorno) do
    create(:transaction, user: user, description: "ESTORNO LOJA", amount: 40,
      transaction_type: "credit", occurred_on: Date.new(2026, 6, 6))
  end
  let!(:salario) do
    create(:transaction, user: user, description: "SALARIO", amount: 5000,
      transaction_type: "credit", category: renda, occurred_on: Date.new(2026, 6, 1))
  end

  before { task.reenable }

  def run_task(env = {})
    original = $stdout
    $stdout = StringIO.new
    env.each { |k, v| ENV[k] = v }
    task.invoke
    $stdout.string
  ensure
    env.each_key { |k| ENV.delete(k) }
    $stdout = original
  end

  it "com DRY_RUN relata e não grava nada" do
    out = run_task("DRY_RUN" => "1")

    expect(out).to include("DRY RUN")
    expect(out).to include("2026-06")
    expect(boleto.reload.kind).to eq("regular")
    expect(estorno.reload.kind).to eq("regular")
  end

  it "sem DRY_RUN marca pagamento (sem categoria) e estorno, e não mexe no resto" do
    run_task

    expect(boleto.reload).to have_attributes(kind: "card_payment", category_id: nil)
    expect(estorno.reload.kind).to eq("refund")
    expect(salario.reload).to have_attributes(kind: "regular", category_id: renda.id)
  end

  it "rodar duas vezes não muda mais nada" do
    run_task
    expect { run_task }.not_to(change { Transaction.order(:id).pluck(:kind, :category_id) })
  end
end
