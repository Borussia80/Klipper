require "rails_helper"

RSpec.describe TransferService do
  let(:user) { create(:user) }
  let(:source) { create(:account, user: user, opening_balance: 100) }
  let(:destination) { create(:account, user: user, opening_balance: 10) }

  it "creates both ledger entries atomically and links them" do
    result = described_class.new(user, source_account: source, destination_account: destination,
      amount: 40, occurred_on: Date.new(2026, 10, 20), description: "Reserva").create

    expect(result.debit).to have_attributes(kind: "transfer", transaction_type: "debit", amount: 40)
    expect(result.credit).to have_attributes(kind: "transfer", transaction_type: "credit", amount: 40)
    expect(result.debit.transfer_pair_id).to eq(result.credit.transfer_pair_id)
    expect(source.reload.current_balance).to eq(60)
    expect(destination.reload.current_balance).to eq(50)
  end

  it "rejects the same source and destination without persisting either side" do
    expect {
      described_class.new(user, source_account: source, destination_account: source,
        amount: 40, occurred_on: Date.new(2026, 10, 20), description: "Inválida").create
    }.to raise_error(TransferService::InvalidTransfer)

    expect(user.transactions).to be_empty
  end

  it "edits both sides of an existing transfer as one unit" do
    created = described_class.new(user, source_account: source, destination_account: destination,
      amount: 40, occurred_on: Date.new(2026, 10, 20), description: "Reserva").create

    result = described_class.update(created.debit, amount: 25, description: "Reserva mensal", status: "conciliado")

    expect(result.debit).to have_attributes(amount: 25, description: "Reserva mensal", status: "conciliado")
    expect(result.credit).to have_attributes(amount: 25, description: "Reserva mensal", status: "conciliado")
    expect(source.reload.current_balance).to eq(75)
    expect(destination.reload.current_balance).to eq(35)
  end
end
