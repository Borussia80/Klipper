module BankImport
  class PreviewSerializer
    def initialize(user, account_id:)
      @user = user
      @account_id = account_id
    end

    def serialize(rows)
      suggestions = cardholder_suggestions(rows)
      own_transfer_suggestions = own_transfer_suggestions(rows)

      rows.each_with_index.map do |row, index|
        serialize_row(row, suggestions, own_transfer_suggestions[index])
      end
    end

    private

    def cardholder_suggestions(rows)
      members = @user.members.active.to_a
      rows.filter_map { |row| row.metadata[:cardholder] }.uniq.index_with do |cardholder|
        MemberMatcher.match(cardholder, members)&.id
      end
    end

    def own_transfer_suggestions(rows)
      identity = @user.own_identity
      return {} unless identity

      dates = rows.map(&:occurred_on)
      return {} if dates.empty?

      file_rows = rows.each_with_index.map do |row, index|
        { account_key: @account_id, occurred_on: row.occurred_on, description: row.description, amount: row.amount,
          source: :file, source_index: index }
      end
      existing_rows = @user.transactions.where.not(account_id: @account_id)
                           .where(occurred_on: (dates.min - 3)..(dates.max + 3)).map do |transaction|
        { account_key: transaction.account_id, occurred_on: transaction.occurred_on, description: transaction.description,
          amount: transaction.transaction_type == "credit" ? transaction.amount : -transaction.amount, source: :existing }
      end
      matched_rows = OwnTransferMatcher.call(file_rows + existing_rows, identity:)

      file_rows.each_with_index.to_h do |row, index|
        suggestion = row[:own_transfer]
        # to_link e investment não têm par (pair_index nil): sem ponta para apontar.
        counterpart = suggestion && suggestion[:pair_index] && matched_rows[suggestion[:pair_index]]
        [ index, serialize_own_transfer(suggestion, counterpart) ]
      end
    end

    def serialize_own_transfer(suggestion, counterpart)
      return unless suggestion

      { state: suggestion[:state].to_s, counterpart: counterpart&.fetch(:source)&.to_s }
    end

    # member_id fica de fora do canonical (RowSigner/SEC-17) de propósito: os outros 5 campos são
    # fato financeiro que tem que rastrear ao documento original, mas member_id é sugestão editável.
    def serialize_row(row, suggestions, own_transfer)
      canonical = {
        occurred_on: row.occurred_on.iso8601,
        description: row.description,
        amount: row.amount.to_s("F"),
        installment_number: row.installment_number,
        installment_total: row.installment_total
      }

      canonical.merge(
        page: row.page,
        metadata: row.metadata,
        suggested_member_id: suggestions[row.metadata[:cardholder]],
        own_transfer:,
        token: RowSigner.sign(canonical)
      )
    end
  end
end
