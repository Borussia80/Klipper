require "rails_helper"

# D1: kind diz o que o lançamento é; status diz se já aconteceu (L-1, L-2).
RSpec.describe Transaction, "kind e status", type: :model do
  let(:user) { create(:user) }

  it "nasce regular e efetivado" do
    t = create(:transaction, user: user)

    expect(t.kind).to eq("regular")
    expect(t.status).to eq("efetivado")
  end

  it "recusa kind e status desconhecidos" do
    expect(build(:transaction, user: user, kind: "presente")).not_to be_valid
    expect(build(:transaction, user: user, status: "talvez")).not_to be_valid
  end

  it "estorno é sempre crédito" do
    expect(build(:transaction, user: user, kind: "refund", transaction_type: "debit")).not_to be_valid
    expect(build(:transaction, user: user, kind: "refund", transaction_type: "credit")).to be_valid
  end

  # O formulário do front ainda envia transaction_type "transfer"; o lançamento
  # tem de sair de receita e despesa mesmo assim.
  it "transaction_type transfer vira kind transfer" do
    t = create(:transaction, user: user, transaction_type: "transfer")

    expect(t.kind).to eq("transfer")
  end

  describe ".countable" do
    it "inclui regular e estorno efetivados; exclui transferência, pagamento de fatura, ajuste e previsto" do
      regular  = create(:transaction, user: user)
      estorno  = create(:transaction, user: user, kind: "refund", transaction_type: "credit")
      create(:transaction, user: user, kind: "transfer")
      create(:transaction, user: user, kind: "card_payment")
      create(:transaction, user: user, kind: "adjustment")
      create(:transaction, user: user, status: "previsto")

      expect(user.transactions.countable).to contain_exactly(regular, estorno)
    end
  end
end
