class CsvImportService
  require 'csv'

  ImportResult = Struct.new(:imported, :errors, keyword_init: true)

  def initialize(user, file_io, account_id: nil)
    @user = user
    @file_io = file_io
    @account_id = account_id
  end

  def call
    rows = CSV.parse(@file_io.read, headers: true, encoding: 'UTF-8')
    imported = 0
    errors = []

    rows.each_with_index do |row, i|
      result = import_row(row)
      if result[:error]
        errors << "Linha #{i + 2}: #{result[:error]}"
      else
        imported += 1
      end
    end

    ImportResult.new(imported: imported, errors: errors)
  rescue CSV::MalformedCSVError => e
    ImportResult.new(imported: 0, errors: ["CSV inválido: #{e.message}"])
  end

  private

  def import_row(row)
    raw_date  = row["Data"]&.strip
    desc      = row["Descrição"]&.strip
    raw_value = row["Valor"]&.strip&.gsub(',', '.')

    return { error: "Dados incompletos" } if raw_date.blank? || desc.blank? || raw_value.blank?

    value = raw_value.to_f
    occurred_on = Date.strptime(raw_date, "%d/%m/%Y")
    tx_type = value >= 0 ? "credit" : "debit"
    amount  = value.abs

    category = AutoCategorizerService.call(desc, @user)

    @user.transactions.create!(
      description:      desc,
      amount:           amount,
      transaction_type: tx_type,
      occurred_on:      occurred_on,
      category:         category,
      account_id:       @account_id
    )
    { ok: true }
  rescue Date::Error
    { error: "Data inválida: #{row['Data']}" }
  rescue ActiveRecord::RecordInvalid => e
    { error: e.message }
  end
end
