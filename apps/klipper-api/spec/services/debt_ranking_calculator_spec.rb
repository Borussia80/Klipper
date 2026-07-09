require "rails_helper"

RSpec.describe DebtRankingCalculator, type: :service do
  let(:user) { create(:user) }

  subject(:ranking) { described_class.new(user).ranking }

  it "reproduces the real Itaú Personnalité invoice figures within rounding tolerance" do
    create(:account, :with_debt_data, user: user)

    row = ranking.first
    expect(row[:saldo_fatura_atual]).to eq(9603.90)
    expect(row[:saldo_projetado_proximo_mes]).to be_within(1.0).of(10_780.76)
  end

  it "excludes cards without saldo_fatura_atual or juros_rotativo_am" do
    create(:account, :credit_card, user: user, saldo_fatura_atual: 500)
    create(:account, :credit_card, user: user)
    create(:account, user: user)

    expect(ranking).to be_empty
  end

  it "excludes cards from other users" do
    other_user = create(:user)
    create(:account, :with_debt_data, user: other_user)

    expect(ranking).to be_empty
  end

  it "ranks by encargos (absolute R$ cost), not by rate alone" do
    high_balance_low_rate = create(:account, :credit_card, user: user, name: "Alto saldo",
      saldo_fatura_atual: 9000, pagamento_minimo: 0, juros_rotativo_am: 5, iof_projetado: 0)
    low_balance_high_rate = create(:account, :credit_card, user: user, name: "Baixo saldo",
      saldo_fatura_atual: 200, pagamento_minimo: 0, juros_rotativo_am: 15, iof_projetado: 0)

    expect(ranking.map { |r| r[:account_id] })
      .to eq([ high_balance_low_rate.id, low_balance_high_rate.id ])
  end

  it "does not let the projected balance go negative when pagamento_minimo exceeds the saldo" do
    create(:account, :credit_card, user: user,
      saldo_fatura_atual: 100, pagamento_minimo: 500, juros_rotativo_am: 10, iof_projetado: 0)

    row = ranking.first
    expect(row[:encargos]).to eq(0.0)
    expect(row[:saldo_projetado_proximo_mes]).to eq(100.0)
  end

  it "treats a missing pagamento_minimo as zero (financia o saldo integral)" do
    create(:account, :credit_card, user: user,
      saldo_fatura_atual: 1000, juros_rotativo_am: 10, iof_projetado: 0)

    row = ranking.first
    expect(row[:encargos]).to eq(100.0)
    expect(row[:saldo_projetado_proximo_mes]).to eq(1100.0)
  end

  it "never has to guard against negative rates or balances, since the model rejects them" do
    account = build(:account, :with_debt_data, user: user, juros_rotativo_am: -5)

    expect(account).not_to be_valid
    expect(account.errors[:juros_rotativo_am]).to be_present
  end

  it "excludes inactive credit cards even when debt data is present" do
    create(:account, :with_debt_data, user: user, active: false)

    expect(ranking).to be_empty
  end

  it "breaks ties in encargos deterministically by saldo_fatura_atual, then account_id" do
    lower_id_same_saldo = create(:account, :credit_card, user: user, name: "Primeiro criado",
      saldo_fatura_atual: 1000, pagamento_minimo: 0, juros_rotativo_am: 10, iof_projetado: 0)
    higher_id_same_saldo = create(:account, :credit_card, user: user, name: "Segundo criado",
      saldo_fatura_atual: 1000, pagamento_minimo: 0, juros_rotativo_am: 10, iof_projetado: 0)
    higher_saldo_same_encargos = create(:account, :credit_card, user: user, name: "Saldo maior",
      saldo_fatura_atual: 2000, pagamento_minimo: 1000, juros_rotativo_am: 10, iof_projetado: 0)

    expect(ranking.map { |r| r[:account_id] })
      .to eq([ higher_saldo_same_encargos.id, lower_id_same_saldo.id, higher_id_same_saldo.id ])
  end
end
