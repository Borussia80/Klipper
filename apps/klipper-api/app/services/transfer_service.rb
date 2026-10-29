class TransferService
  InvalidTransfer = Class.new(StandardError)
  LockedEntry = Class.new(StandardError)
  Result = Data.define(:debit, :credit)

  def initialize(user, source_account:, destination_account:, amount:, occurred_on:, description:, status: "efetivado")
    @user = user
    @source_account = source_account
    @destination_account = destination_account
    @amount = amount
    @occurred_on = occurred_on
    @description = description
    @status = status
  end

  def create
    validate!
    Transaction.transaction do
      pair_id = SecureRandom.uuid
      debit = build_entry(@source_account, "debit", pair_id).tap(&:save!)
      credit = build_entry(@destination_account, "credit", pair_id).tap(&:save!)
      audit!("TRANSFER_CREATED", pair_id)
      Result.new(debit, credit)
    end
  end

  def self.soft_delete(transaction)
    # Conciliado não se exclui (spec 03, L-22): desconcilia antes, ou reverte.
    if entries_for(transaction).exists?(status: "conciliado")
      raise LockedEntry, "Lançamento conciliado não pode ser excluído; desconcilie antes"
    end

    Transaction.transaction do
      entries_for(transaction).update_all(deleted_at: Time.current, updated_at: Time.current)
      audit(transaction.user, "TRANSACTION_DELETED", transaction.transfer_pair_id || transaction.id)
    end
  end

  def self.update(transaction, attributes)
    Transaction.transaction do
      entries = entries_for(transaction).to_a
      raise InvalidTransfer, "Transferência incompleta" unless entries.length == 2

      entries.each { |entry| entry.update!(attributes.slice(:amount, :description, :occurred_on, :status)) }
      audit(transaction.user, "TRANSFER_UPDATED", transaction.transfer_pair_id)
      Result.new(entries.find(&:debit?), entries.find(&:credit?))
    end
  end

  def self.restore(transaction)
    Transaction.transaction do
      entries_for(transaction).update_all(deleted_at: nil, updated_at: Time.current)
      audit(transaction.user, "TRANSACTION_RESTORED", transaction.transfer_pair_id || transaction.id)
    end
  end

  def self.entries_for(transaction)
    return Transaction.where(id: transaction.id) if transaction.transfer_pair_id.blank?

    transaction.user.transactions.where(transfer_pair_id: transaction.transfer_pair_id)
  end

  def self.audit(user, event_type, subject)
    AuditLog.create!(user: user, event_type: event_type, record_count: 1, metadata: { subject: subject })
  end

  private

  def validate!
    raise InvalidTransfer, "A origem e o destino devem ser diferentes" if @source_account.id == @destination_account.id
    raise InvalidTransfer, "Valor deve ser maior que zero" unless @amount.to_d.positive?
    raise InvalidTransfer, "Conta inválida" unless [ @source_account, @destination_account ].all? { |account| account.user_id == @user.id && account.active? }
  end

  def build_entry(account, transaction_type, pair_id)
    @user.transactions.build(
      account: account,
      description: @description,
      amount: @amount,
      occurred_on: @occurred_on,
      kind: "transfer",
      status: @status,
      transaction_type: transaction_type,
      transfer_pair_id: pair_id
    )
  end

  def audit!(event_type, subject)
    self.class.audit(@user, event_type, subject)
  end
end
