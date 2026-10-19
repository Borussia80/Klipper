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

    it "creates identical rows in one account import with sequential external ids" do
      account = create(:account, user: user)
      ordinals = Hash.new(0)
      writer = described_class.new(user, account_id: account.id, ordinals: ordinals)

      first = writer.write!(description: "CAFÉ X", amount: BigDecimal("-5.00"), occurred_on: Date.new(2026, 6, 25))
      second = writer.write!(description: "CAFE X", amount: BigDecimal("-5.00"), occurred_on: Date.new(2026, 6, 25))

      expect([ first.external_id, second.external_id ]).to contain_exactly(
        BankImport::ExternalId.for_row(
          { occurred_on: Date.new(2026, 6, 25), description: "CAFÉ X", amount: BigDecimal("-5.00") },
          account_key: account.id.to_s, ordinal: 1
        ),
        BankImport::ExternalId.for_row(
          { occurred_on: Date.new(2026, 6, 25), description: "CAFE X", amount: BigDecimal("-5.00") },
          account_key: account.id.to_s, ordinal: 2
        )
      )
    end

    it "treats a unique-index race as a duplicate" do
      account = create(:account, user: user)
      writer = described_class.new(user, account_id: account.id)
      allow(user.transactions).to receive(:create!).and_raise(ActiveRecord::RecordNotUnique)

      result = writer.write!(description: "Loja X", amount: BigDecimal("-10.00"), occurred_on: Date.new(2026, 6, 25))

      expect(result).to eq(described_class::DUPLICATE)
    end

    it "leaves external_id nil without an account" do
      tx = described_class.new(user).write!(
        description: "Loja X", amount: BigDecimal("-10.00"), occurred_on: Date.new(2026, 6, 25)
      )

      expect(tx.external_id).to be_nil
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

    # D1 (spec 03, L-12): pagamento de fatura move dinheiro entre contas próprias.
    it "grava pagamento de fatura como card_payment e sem categoria" do
      create(:category, :income, user: user, name: "Renda")

      tx = described_class.new(user).write!(
        description: "PAG BOLETO NU PAGAMENTOS SA", amount: BigDecimal("-320.00"), occurred_on: Date.new(2026, 6, 25)
      )

      expect(tx.kind).to eq("card_payment")
      expect(tx.category).to be_nil
    end

    it "grava estorno como refund, ainda categorizado pela regra" do
      create(:category, user: user, name: "Lazer")

      tx = described_class.new(user).write!(
        description: "ESTORNO NETFLIX", amount: BigDecimal("39.90"), occurred_on: Date.new(2026, 6, 25)
      )

      expect(tx.kind).to eq("refund")
      expect(tx.transaction_type).to eq("credit")
      expect(tx.category&.name).to eq("Lazer")
    end
  end
end
