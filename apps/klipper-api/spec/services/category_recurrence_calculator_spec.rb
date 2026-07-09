require "rails_helper"

RSpec.describe CategoryRecurrenceCalculator, type: :service do
  let(:user)     { create(:user) }
  let(:other_user) { create(:user) }
  let(:account)  { create(:account, user: user) }
  let(:category) { create(:category, user: user, name: "Aluguel", icon: "home") }
  let(:reference_date) { Date.new(2026, 7, 15) }

  def debit_in(year:, month:, cat: category, owner: user, acc: account)
    create(:transaction, user: owner, account: acc, category: cat,
      transaction_type: "debit", amount: 100, occurred_on: Date.new(year, month, 5))
  end

  def credit_in(year:, month:, cat: category, owner: user, acc: account)
    create(:transaction, user: owner, account: acc, category: cat,
      transaction_type: "credit", amount: 100, occurred_on: Date.new(year, month, 5))
  end

  subject(:result) do
    described_class.new(user, category, months: months, reference_date: reference_date).call
  end

  context "with the default 6-month window" do
    let(:months) { CategoryRecurrenceCalculator::DEFAULT_MONTHS }

    it "classifies as rotineiro when present in all 6 of the last 6 months" do
      [ [ 2026, 2 ], [ 2026, 3 ], [ 2026, 4 ], [ 2026, 5 ], [ 2026, 6 ], [ 2026, 7 ] ].each do |y, m|
        debit_in(year: y, month: m)
      end

      expect(result[:months_present]).to eq(6)
      expect(result[:months_total]).to eq(6)
      expect(result[:recorrencia]).to eq("rotineiro")
    end

    it "classifies as rotineiro when present in 4 of 6 months (66%)" do
      [ [ 2026, 4 ], [ 2026, 5 ], [ 2026, 6 ], [ 2026, 7 ] ].each { |y, m| debit_in(year: y, month: m) }

      expect(result[:months_present]).to eq(4)
      expect(result[:recorrencia]).to eq("rotineiro")
    end

    it "classifies as ocasional when present in 2 of 6 months (33%)" do
      [ [ 2026, 6 ], [ 2026, 7 ] ].each { |y, m| debit_in(year: y, month: m) }

      expect(result[:months_present]).to eq(2)
      expect(result[:recorrencia]).to eq("ocasional")
    end

    it "classifies as pontual when present in 1 of 6 months (16%)" do
      debit_in(year: 2026, month: 7)

      expect(result[:months_present]).to eq(1)
      expect(result[:recorrencia]).to eq("pontual")
    end

    it "classifies as pontual when there are no transactions in the window" do
      expect(result[:months_present]).to eq(0)
      expect(result[:recorrencia]).to eq("pontual")
    end

    it "only counts debit transactions as present, not credit" do
      credit_in(year: 2026, month: 7)
      credit_in(year: 2026, month: 6)

      expect(result[:months_present]).to eq(0)
      expect(result[:recorrencia]).to eq("pontual")
    end

    it "is scoped to the given user and does not leak other users' transactions" do
      other_account = create(:account, user: other_user)
      other_category = create(:category, user: other_user, name: "Aluguel", icon: "home")
      [ [ 2026, 2 ], [ 2026, 3 ], [ 2026, 4 ], [ 2026, 5 ], [ 2026, 6 ], [ 2026, 7 ] ].each do |y, m|
        debit_in(year: y, month: m, cat: other_category, owner: other_user, acc: other_account)
      end

      expect(result[:months_present]).to eq(0)
      expect(result[:recorrencia]).to eq("pontual")
    end
  end

  context "at the exact classification boundaries with a 10-month window" do
    let(:months) { 10 }

    it "classifies exactly 60% (6 of 10) as rotineiro" do
      (0...6).each { |i| d = reference_date.prev_month(i); debit_in(year: d.year, month: d.month) }

      expect(result[:ratio]).to eq(0.6)
      expect(result[:recorrencia]).to eq("rotineiro")
    end

    it "classifies exactly 30% (3 of 10) as ocasional" do
      (0...3).each { |i| d = reference_date.prev_month(i); debit_in(year: d.year, month: d.month) }

      expect(result[:ratio]).to eq(0.3)
      expect(result[:recorrencia]).to eq("ocasional")
    end

    it "classifies just under 30% (2 of 10) as pontual" do
      (0...2).each { |i| d = reference_date.prev_month(i); debit_in(year: d.year, month: d.month) }

      expect(result[:ratio]).to eq(0.2)
      expect(result[:recorrencia]).to eq("pontual")
    end
  end

  context "with a custom months: override" do
    let(:months) { 3 }

    it "respects the overridden window size" do
      debit_in(year: 2026, month: 7)
      debit_in(year: 2026, month: 6)

      expect(result[:months_total]).to eq(3)
      expect(result[:months_present]).to eq(2)
      expect(result[:recorrencia]).to eq("rotineiro")
    end
  end
end
