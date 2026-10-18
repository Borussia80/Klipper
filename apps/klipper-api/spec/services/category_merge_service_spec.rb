require "rails_helper"

# Fatia 1 de UX: mesclar a categoria de origem na de destino, tudo ou nada.
# Escritos antes da implementação; falham até o CategoryMergeService existir.
RSpec.describe CategoryMergeService, type: :service do
  let(:user)    { create(:user) }
  let(:account) { create(:account, user: user) }
  let!(:origem)  { create(:category, user: user, name: "Alimentação") }
  let!(:destino) { create(:category, user: user, name: "Comida") }

  def merge(source = origem, into = destino)
    described_class.call(source: source, into: into)
  end

  it "move os lançamentos da origem para o destino" do
    t = create(:transaction, user: user, account: account, category: origem, occurred_on: Date.new(2026, 6, 10))

    merge

    expect(t.reload.category).to eq(destino)
  end

  it "move orçamentos e, quando os dois têm orçamento no mesmo mês, soma os limites" do
    create(:budget, user: user, category: origem,  amount_limit: 300, period_year: 2026, period_month: 6)
    create(:budget, user: user, category: destino, amount_limit: 500, period_year: 2026, period_month: 6)
    create(:budget, user: user, category: origem,  amount_limit: 200, period_year: 2026, period_month: 7)

    merge

    junho = user.budgets.find_by(period_year: 2026, period_month: 6)
    julho = user.budgets.find_by(period_year: 2026, period_month: 7)
    expect(user.budgets.where(category: origem)).to be_empty
    expect(junho.category).to eq(destino)
    expect(junho.amount_limit).to eq(800)
    expect(julho.category).to eq(destino)
  end

  it "repassa quem era reembolsado pela origem" do
    renda_origem  = create(:category, :income, user: user, name: "Reembolso plano")
    renda_destino = create(:category, :income, user: user, name: "Reembolsos")
    saude = create(:category, user: user, name: "Saúde", reimbursed_by_category: renda_origem)

    merge(renda_origem, renda_destino)

    expect(saude.reload.reimbursed_by_category).to eq(renda_destino)
  end

  it "desativa a origem e guarda para onde foi mesclada" do
    merge

    origem.reload
    expect(origem.active).to be(false)
    expect(origem.merged_into_id).to eq(destino.id)
  end

  it "leva as filhas da origem para o destino raiz" do
    filha = create(:category, user: user, name: "Restaurante", parent: origem)

    merge

    expect(filha.reload.parent).to eq(destino)
  end

  it "recusa mesclar categoria com filhas em um destino que é filha" do
    create(:category, user: user, name: "Restaurante", parent: origem)
    destino_filha = create(:category, user: user, name: "Lanches", parent: destino)

    expect { merge(origem, destino_filha) }.to raise_error(CategoryMergeService::InvalidMerge)
  end

  it "recusa mesclar em si mesma, em categoria de outro usuário ou de outro tipo" do
    expect { merge(origem, origem) }.to raise_error(CategoryMergeService::InvalidMerge)
    expect { merge(origem, create(:category, name: "Alheia")) }.to raise_error(CategoryMergeService::InvalidMerge)
    expect { merge(origem, create(:category, :income, user: user)) }.to raise_error(CategoryMergeService::InvalidMerge)
  end

  it "não deixa nada mudado se falhar no meio" do
    t = create(:transaction, user: user, account: account, category: origem, occurred_on: Date.new(2026, 6, 10))
    create(:budget, user: user, category: origem, amount_limit: 300, period_year: 2026, period_month: 6)
    allow_any_instance_of(Category).to receive(:update!).and_raise(ActiveRecord::RecordInvalid)

    expect { merge }.to raise_error(ActiveRecord::RecordInvalid)

    expect(t.reload.category).to eq(origem)
    expect(user.budgets.first.category).to eq(origem)
    expect(origem.reload.active).to be(true)
  end

  it "a regra automática que achava a origem pelo nome passa a devolver o destino" do
    merge

    expect(AutoCategorizerService.call("IFOOD *PEDIDO", user)).to eq(destino)
  end
end
