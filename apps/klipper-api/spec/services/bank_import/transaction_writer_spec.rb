require "rails_helper"

RSpec.describe BankImport::TransactionWriter, type: :service do
  let(:user) { create(:user) }

  describe "#write!" do
    it "creates a transaction without a member when member_id is not given" do
      writer = described_class.new(user)

      tx = writer.write!(description: "Loja X", amount: BigDecimal("-10.00"), occurred_on: Date.new(2026, 6, 25))

      expect(tx).to be_persisted
      expect(tx.member_id).to be_nil
    end

    it "persists the given member_id on the created transaction" do
      member = create(:member, user: user)
      writer = described_class.new(user)

      tx = writer.write!(
        description: "Loja X", amount: BigDecimal("-10.00"), occurred_on: Date.new(2026, 6, 25),
        member_id: member.id
      )

      expect(tx.member_id).to eq(member.id)
    end

    it "returns :duplicate and does not create a second transaction for an identical write" do
      writer = described_class.new(user)
      writer.write!(description: "Loja X", amount: BigDecimal("-10.00"), occurred_on: Date.new(2026, 6, 25))

      result = writer.write!(description: "Loja X", amount: BigDecimal("-10.00"), occurred_on: Date.new(2026, 6, 25))

      expect(result).to eq(described_class::DUPLICATE)
      expect(user.transactions.count).to eq(1)
    end

    it "does not treat a debit and a credit with the same amount/date/description as duplicates" do
      writer = described_class.new(user)
      writer.write!(description: "Estorno", amount: BigDecimal("-10.00"), occurred_on: Date.new(2026, 6, 25))

      result = writer.write!(description: "Estorno", amount: BigDecimal("10.00"), occurred_on: Date.new(2026, 6, 25))

      expect(result).to be_a(Transaction)
      expect(user.transactions.count).to eq(2)
    end

    it "does not dedupe across different users" do
      other_user = create(:user)
      described_class.new(user).write!(description: "Loja X", amount: BigDecimal("-10.00"), occurred_on: Date.new(2026, 6, 25))

      result = described_class.new(other_user).write!(description: "Loja X", amount: BigDecimal("-10.00"), occurred_on: Date.new(2026, 6, 25))

      expect(result).to be_a(Transaction)
    end
  end
end
