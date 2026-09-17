require "rails_helper"

RSpec.describe NaturezaSplitCalculator do
  let(:user) { create(:user) }
  let(:fixo) { create(:category, user: user, name: "Aluguel", natureza: "fixo") }
  let(:variavel) { create(:category, user: user, name: "Mercado", natureza: "variavel") }

  def calculator(**overrides)
    described_class.new(user, **{ year: 2026, month: 6 }.merge(overrides))
  end

  describe "#call" do
    before do
      create(:transaction, user: user, amount: 300.00, transaction_type: "debit",
             occurred_on: "2026-06-05", category: fixo)
      create(:transaction, user: user, amount: 100.00, transaction_type: "debit",
             occurred_on: "2026-06-12", category: variavel)
    end

    it "splits the month's debits by the category's natureza" do
      result = calculator.call

      expect(result[:total]).to eq(400.00)
      expect(result[:by_natureza]).to include(
        { natureza: "fixo", total: 300.00, pct: 75.0 },
        { natureza: "variavel", total: 100.00, pct: 25.0 }
      )
    end

    # O gráfico do front desenha uma fatia por natureza. Uma natureza sem
    # lançamento no mês tem que vir zerada em vez de sumir da lista, senão a
    # fatia desaparece e o gráfico muda de forma de um mês para o outro.
    it "returns every natureza, including the ones with no transactions" do
      rows = calculator.call[:by_natureza]

      expect(rows.map { |r| r[:natureza] }).to eq(Category::NATUREZAS)
      expect(rows.find { |r| r[:natureza] == "cartao_parcelamento" })
        .to eq(natureza: "cartao_parcelamento", total: 0.0, pct: 0.0)
    end

    it "ignores credits, counting only what was spent" do
      create(:transaction, user: user, amount: 9000.00, transaction_type: "credit",
             occurred_on: "2026-06-01", category: fixo)

      expect(calculator.call[:total]).to eq(400.00)
    end

    it "ignores other months" do
      create(:transaction, user: user, amount: 777.00, transaction_type: "debit",
             occurred_on: "2026-05-05", category: fixo)

      expect(calculator.call[:total]).to eq(400.00)
    end

    it "restricts to a member when member_id is given" do
      member = create(:member, user: user)
      create(:transaction, user: user, member: member, amount: 50.00,
             transaction_type: "debit", occurred_on: "2026-06-20", category: variavel)

      result = calculator(member_id: member.id).call

      expect(result[:total]).to eq(50.00)
      expect(result[:by_natureza].find { |r| r[:natureza] == "variavel" }[:pct]).to eq(100.0)
    end
  end

  describe "with no transactions in the window" do
    # Divisão por zero: sem gasto nenhum o pct de cada natureza tem que ser
    # 0.0, não NaN nem erro.
    it "returns zero percentages instead of dividing by zero" do
      result = calculator.call

      expect(result[:total]).to eq(0.0)
      expect(result[:by_natureza].map { |r| r[:pct] }).to all(eq(0.0))
      expect(result[:by_natureza].size).to eq(Category::NATUREZAS.size)
    end

    it "counts zero records" do
      expect(calculator.record_count).to eq(0)
    end
  end

  describe "#record_count" do
    it "counts only the debits that compose the split" do
      create(:transaction, user: user, amount: 300.00, transaction_type: "debit",
             occurred_on: "2026-06-05", category: fixo)
      create(:transaction, user: user, amount: 9000.00, transaction_type: "credit",
             occurred_on: "2026-06-01", category: fixo)

      expect(calculator.record_count).to eq(1)
    end
  end
end
