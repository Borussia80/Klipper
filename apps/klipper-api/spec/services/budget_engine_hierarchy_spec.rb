require "rails_helper"

# Fatia 1 de UX, regra de orçamento pai × filha sem dupla contagem:
# - gasto do pai = lançamentos no pai + nas filhas; gasto da filha = só os dela;
# - limite da filha é sub-envelope dentro do pai, não soma ao total;
# - limite efetivo do grupo = limite do pai, se houver; senão, soma das filhas;
# - total do mês conta cada grupo e cada lançamento uma vez só.
# Escritos antes da implementação; falham até parent_id e BudgetEngine#totals.
RSpec.describe BudgetEngine, "pai e filhas", type: :service do
  let(:user)    { create(:user) }
  let(:account) { create(:account, user: user) }
  let(:moradia) { create(:category, user: user, name: "Moradia") }
  let(:aluguel) { create(:category, user: user, name: "Aluguel", parent: moradia) }
  let(:luz)     { create(:category, user: user, name: "Luz", parent: moradia) }

  subject(:engine) { described_class.new(user, 2026, 6) }

  def gasto(categoria, valor)
    create(:transaction, user: user, account: account, category: categoria,
      amount: valor, transaction_type: "debit", occurred_on: Date.new(2026, 6, 10))
  end

  def limite(categoria, valor)
    create(:budget, user: user, category: categoria, amount_limit: valor, period_year: 2026, period_month: 6)
  end

  def linha(categoria)
    engine.summary.find { |r| r[:category_id] == categoria.id }
  end

  it "gasto do pai soma o lançado nele e nas filhas; o da filha, só o dela" do
    limite(moradia, 3000)
    limite(aluguel, 2000)
    gasto(moradia, 100)
    gasto(aluguel, 1800)
    gasto(luz, 150)

    expect(linha(moradia)[:spent]).to eq(2050)
    expect(linha(aluguel)[:spent]).to eq(1800)
  end

  it "com limite no pai, o total usa o limite do pai e não soma o das filhas" do
    limite(moradia, 3000)
    limite(aluguel, 2000)
    gasto(aluguel, 1800)
    gasto(luz, 150)

    expect(engine.totals).to include(amount_limit: 3000, spent: 1950)
  end

  it "sem limite no pai, o limite do grupo é a soma das filhas" do
    limite(aluguel, 2000)
    limite(luz, 200)
    gasto(aluguel, 1800)
    gasto(luz, 150)

    expect(engine.totals).to include(amount_limit: 2200, spent: 1950)
  end

  it "filha sem limite com gasto entra no gasto do pai" do
    limite(moradia, 3000)
    gasto(luz, 150)

    expect(linha(moradia)[:spent]).to eq(150)
    expect(linha(luz)).to be_nil
  end

  it "o gasto total do mês é a soma dos lançamentos, cada um uma vez" do
    mercado = create(:category, user: user, name: "Mercado")
    limite(moradia, 3000)
    limite(aluguel, 2000)
    limite(mercado, 800)
    gasto(moradia, 100)
    gasto(aluguel, 1800)
    gasto(mercado, 500)

    expect(engine.totals[:spent]).to eq(user.transactions.debits.in_month(2026, 6).sum(:amount))
    expect(engine.totals[:amount_limit]).to eq(3800)
  end

  it "avisa quando as filhas somam mais que o limite do pai, sem bloquear" do
    limite(moradia, 1000)
    limite(aluguel, 900)
    limite(luz, 200)

    expect(linha(moradia)[:children_over_parent]).to be(true)
  end
end
