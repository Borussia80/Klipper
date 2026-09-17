require "rails_helper"

RSpec.describe MonthlySummaryCalculator do
  let(:user) { create(:user) }
  let(:cat) { create(:category, user: user, name: "Alimentação", icon: "alimentacao") }

  before do
    create(:transaction, user: user, amount: 150.00, transaction_type: "debit",
           occurred_on: "2026-06-10", category: cat)
    create(:transaction, user: user, amount: 120.50, transaction_type: "debit",
           occurred_on: "2026-06-15", category: nil)
    create(:transaction, user: user, amount: 5000.00, transaction_type: "credit",
           occurred_on: "2026-06-05", category: nil)
    create(:transaction, user: user, amount: 999.00, transaction_type: "debit",
           occurred_on: "2026-05-20", category: cat)
  end

  def calculator(**overrides)
    described_class.new(user, **{ year: 2026, month: 6 }.merge(overrides))
  end

  describe "#call" do
    it "sums debits and credits of the requested month only" do
      result = calculator.call

      expect(result[:total_debits]).to eq(270.50)
      expect(result[:total_credits]).to eq(5000.00)
      expect(result[:net]).to eq(4729.50)
    end

    it "groups debits by category, descending by total" do
      rows = calculator.call[:by_category]

      expect(rows.map { |r| r[:total] }).to eq([ 150.00, 120.50 ])
      expect(rows.first).to include(category_id: cat.id, category_name: "Alimentação",
                                    category_icon: "alimentacao", count: 1)
    end

    # Lançamento sem categoria é comum na importação de extrato: ele tem que
    # aparecer no agrupamento, não desaparecer da soma por categoria.
    it "labels uncategorized debits instead of dropping them" do
      row = calculator.call[:by_category].find { |r| r[:category_id].nil? }

      expect(row).to include(category_name: "Sem categoria", category_icon: nil, total: 120.50)
    end

    it "restricts to a member when member_id is given" do
      member = create(:member, user: user)
      create(:transaction, user: user, member: member, amount: 40.00,
             transaction_type: "debit", occurred_on: "2026-06-20", category: cat)

      result = calculator(member_id: member.id).call

      expect(result[:total_debits]).to eq(40.00)
      expect(result[:total_credits]).to eq(0.0)
    end

    it "returns zeros for a month with no transactions" do
      result = calculator(month: 1).call

      expect(result).to eq(total_debits: 0.0, total_credits: 0.0, net: 0.0, by_category: [])
    end
  end

  describe "#record_count" do
    # Fica fora do hash de `call` porque alimenta o log de auditoria de
    # exportação, não o JSON da resposta — e conta débitos e créditos, não só
    # os débitos que compõem o by_category.
    it "counts every transaction in the window, not just the debits" do
      expect(calculator.record_count).to eq(3)
    end

    it "counts zero for a month with no transactions" do
      expect(calculator(month: 1).record_count).to eq(0)
    end
  end
end
