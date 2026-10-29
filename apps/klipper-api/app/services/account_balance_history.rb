class AccountBalanceHistory
  def initialize(account, from:, to:)
    @account = account
    @from = from
    @to = to
  end

  def call
    balance = opening_balance
    entries = transactions.map do |transaction|
      balance += transaction.ledger_delta
      entry(transaction, balance)
    end

    { opening_balance: opening_balance, closing_balance: balance, entries: entries }
  end

  private

  def opening_balance
    @opening_balance ||= @account.balance_at(@from - 1.day) || @account.opening_balance
  end

  def transactions
    @account.transactions.booked.kept
      .where(occurred_on: @from..@to)
      .order(:occurred_on, :id)
  end

  def entry(transaction, balance)
    {
      id: transaction.id,
      occurred_on: transaction.occurred_on,
      description: transaction.description,
      delta: transaction.ledger_delta,
      balance: balance
    }
  end
end
