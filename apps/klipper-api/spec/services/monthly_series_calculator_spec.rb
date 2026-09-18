require "rails_helper"

# O painel mostrava um mês por vez. Para responder "estou melhorando ou
# piorando?" é preciso a série: entradas, saídas e resultado de cada mês da
# janela, inclusive os meses sem nenhum lançamento — buraco na série vira
# leitura errada do gráfico.
RSpec.describe MonthlySeriesCalculator do
  let(:user) { create(:user) }
  let(:member) { create(:member, user: user) }

  before do
    create(:transaction, user: user, amount: 5000.00, transaction_type: "credit", occurred_on: "2026-06-05")
    create(:transaction, user: user, amount: 150.00, transaction_type: "debit", occurred_on: "2026-06-10")
    create(:transaction, user: user, amount: 120.50, transaction_type: "debit", occurred_on: "2026-06-15")
    create(:transaction, user: user, amount: 999.00, transaction_type: "debit", occurred_on: "2026-05-20")
    create(:transaction, user: user, amount: 10.00, transaction_type: "debit", occurred_on: "2026-01-02")
    create(:transaction, user: user, amount: 77.00, transaction_type: "debit", occurred_on: "2025-12-31")
  end

  def calculator(**overrides)
    described_class.new(user, **{ year: 2026, month: 6, months: 6 }.merge(overrides))
  end

  describe "#call" do
    it "returns one point per month of the window, oldest first" do
      points = calculator.call[:points]

      expect(points.length).to eq(6)
      expect(points.map { |p| [ p[:year], p[:month] ] }).to eq(
        [ [ 2026, 1 ], [ 2026, 2 ], [ 2026, 3 ], [ 2026, 4 ], [ 2026, 5 ], [ 2026, 6 ] ]
      )
    end

    it "sums credits, debits and net of each month" do
      points = calculator.call[:points]

      expect(points.last).to include(year: 2026, month: 6, total_credits: 5000.00,
                                     total_debits: 270.50, net: 4729.50)
      expect(points[4]).to include(month: 5, total_credits: 0.0, total_debits: 999.00, net: -999.00)
    end

    # Fevereiro não tem lançamento nenhum: o mês existe na série com zeros, senão
    # o gráfico emenda janeiro em março e o usuário lê uma queda que não houve.
    it "keeps months without any movement as zeroed points" do
      expect(calculator.call[:points][1]).to include(year: 2026, month: 2, total_credits: 0.0,
                                                     total_debits: 0.0, net: 0.0)
    end

    it "ignores months outside the window" do
      points = calculator.call[:points]

      expect(points.map { |p| p[:month] }).not_to include(12)
      expect(points.sum { |p| p[:total_debits] }).to eq(1279.50)
    end

    it "honours a shorter window" do
      points = calculator(months: 3).call[:points]

      expect(points.map { |p| p[:month] }).to eq([ 4, 5, 6 ])
    end

    it "crosses the year boundary" do
      points = described_class.new(user, year: 2026, month: 1, months: 2).call[:points]

      expect(points.map { |p| [ p[:year], p[:month] ] }).to eq([ [ 2025, 12 ], [ 2026, 1 ] ])
      expect(points.first[:total_debits]).to eq(77.00)
    end

    it "filters by member when asked" do
      create(:transaction, user: user, member: member, amount: 33.00,
             transaction_type: "debit", occurred_on: "2026-06-20")

      points = calculator(member_id: member.id).call[:points]

      expect(points.last[:total_debits]).to eq(33.00)
      expect(points.last[:total_credits]).to eq(0.0)
    end

    it "does not leak another user's transactions" do
      other = create(:user)
      create(:transaction, user: other, amount: 900.00, transaction_type: "debit", occurred_on: "2026-06-11")

      expect(calculator.call[:points].last[:total_debits]).to eq(270.50)
    end
  end

  describe "#record_count" do
    it "counts the transactions of the whole window" do
      expect(calculator.record_count).to eq(5)
    end
  end
end
