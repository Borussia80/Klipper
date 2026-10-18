require "rails_helper"

# Fatia 1 de UX (docs/ux-research/05-specs/07-categorias.md): categorias em dois
# níveis. Escritos antes da implementação; falham até a migração de parent_id.
RSpec.describe Category, "hierarquia em dois níveis", type: :model do
  let(:user) { create(:user) }
  let(:pai)  { create(:category, user: user, name: "Moradia", natureza: "fixo") }

  it "aceita uma filha de uma categoria raiz" do
    filha = build(:category, user: user, name: "Aluguel", parent: pai)

    expect(filha).to be_valid
    expect(pai.reload.children).to be_empty
    filha.save!
    expect(pai.reload.children).to contain_exactly(filha)
  end

  it "recusa neta: o pai precisa ser raiz" do
    filha = create(:category, user: user, name: "Aluguel", parent: pai)
    neta  = build(:category, user: user, name: "Caução", parent: filha)

    expect(neta).not_to be_valid
    expect(neta.errors[:parent_id]).to be_present
  end

  it "recusa transformar em filha uma categoria que já tem filhas" do
    create(:category, user: user, name: "Aluguel", parent: pai)
    outro_pai = create(:category, user: user, name: "Casa")

    pai.parent = outro_pai

    expect(pai).not_to be_valid
    expect(pai.errors[:parent_id]).to be_present
  end

  it "recusa ser pai de si mesma" do
    pai.parent_id = pai.id

    expect(pai).not_to be_valid
  end

  it "recusa pai de outro usuário" do
    alheio = create(:category, name: "Moradia")
    filha  = build(:category, user: user, name: "Aluguel", parent: alheio)

    expect(filha).not_to be_valid
  end

  it "recusa pai de outro tipo" do
    receita = create(:category, :income, user: user, name: "Renda")
    filha   = build(:category, user: user, name: "Aluguel", category_type: "expense", parent: receita)

    expect(filha).not_to be_valid
  end

  it "filha herda natureza e tipo do pai, mesmo se vier outro valor" do
    filha = create(:category, user: user, name: "Aluguel", parent: pai, natureza: "variavel")

    expect(filha.natureza).to eq("fixo")
    expect(filha.category_type).to eq("expense")
  end

  it "não deixa excluir pai que tem filhas" do
    create(:category, user: user, name: "Aluguel", parent: pai)

    expect { pai.destroy }.not_to change(Category, :count)
  end
end
