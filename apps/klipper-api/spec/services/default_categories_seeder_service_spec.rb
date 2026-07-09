require "rails_helper"

RSpec.describe DefaultCategoriesSeederService, type: :service do
  let(:user) { create(:user) }

  it "creates one category per default definition" do
    expect { described_class.call(user) }.to change { user.categories.count }.by(DefaultCategoriesSeederService::DEFAULTS.size)
  end

  it "creates valid categories with the expected type/natureza split" do
    described_class.call(user)

    renda = user.categories.find_by(name: "Renda")
    expect(renda.category_type).to eq("income")

    transferencia = user.categories.find_by(name: "Transferência")
    expect(transferencia.category_type).to eq("transfer")

    moradia = user.categories.find_by(name: "Moradia")
    expect(moradia.natureza).to eq("fixo")
  end

  it "is idempotent — running it twice does not duplicate categories" do
    described_class.call(user)

    expect { described_class.call(user) }.not_to(change { user.categories.count })
  end

  it "does not touch categories belonging to other users" do
    other_user = create(:user)
    create(:category, user: other_user, name: "Alimentação")

    expect { described_class.call(user) }.to change { user.categories.count }.by(DefaultCategoriesSeederService::DEFAULTS.size)
  end
end
