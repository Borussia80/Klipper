require "rails_helper"

RSpec.describe AutoCategorizerService, type: :service do
  let(:user) { create(:user) }

  before do
    create(:category, user: user, name: "Alimentação", category_type: "expense", icon: "food")
    create(:category, user: user, name: "Transporte",  category_type: "expense", icon: "car")
    create(:category, user: user, name: "Lazer",       category_type: "expense", icon: "fun")
    create(:category, user: user, name: "Saúde",       category_type: "expense", icon: "health")
  end

  it "matches supermercado to Alimentação" do
    result = described_class.call("Compra no Supermercado Extra", user)
    expect(result&.name).to eq("Alimentação")
  end

  it "matches iFood to Alimentação" do
    result = described_class.call("iFood pedido #123", user)
    expect(result&.name).to eq("Alimentação")
  end

  it "matches Uber to Transporte" do
    result = described_class.call("Uber corrida 22h", user)
    expect(result&.name).to eq("Transporte")
  end

  it "matches Netflix to Lazer" do
    result = described_class.call("NETFLIX.COM", user)
    expect(result&.name).to eq("Lazer")
  end

  # R1: "pagamento" aparece no pagamento da fatura (dos dois lados) e não é renda.
  context "com a categoria Renda" do
    before { create(:category, :income, user: user, name: "Renda") }

    it "não classifica pagamento de fatura como renda" do
      expect(described_class.call("Pagamento em 10 JUN", user)).to be_nil
      expect(described_class.call("PAG BOLETO NU PAGAMENTOS SA", user)).to be_nil
    end

    it "continua classificando salário como renda" do
      expect(described_class.call("SALÁRIO EMPRESA X", user)&.name).to eq("Renda")
    end
  end

  it "returns nil for unknown description" do
    result = described_class.call("Pagamento genérico aleatório", user)
    expect(result).to be_nil
  end

  it "returns nil if user does not have the matching category" do
    user2 = create(:user)
    result = described_class.call("Supermercado Extra", user2)
    expect(result).to be_nil
  end
end
