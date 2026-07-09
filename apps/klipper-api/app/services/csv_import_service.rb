class CsvImportService
  require 'csv'

  ImportResult = Struct.new(:imported, :duplicates, :errors, keyword_init: true)

  def initialize(user, file_io, account_id: nil)
    @user = user
    @file_io = file_io
    @account_id = account_id
  end

  def call
    rows = CSV.parse(@file_io.read, headers: true, encoding: 'UTF-8')
    imported = 0
    duplicates = 0
    errors = []

    rows.each_with_index do |row, i|
      result = import_row(row)
      if result[:error]
        errors << "Linha #{i + 2}: #{result[:error]}"
      elsif result[:duplicate]
        duplicates += 1
      else
        imported += 1
      end
    end

    ImportResult.new(imported: imported, duplicates: duplicates, errors: errors)
  rescue CSV::MalformedCSVError => e
    ImportResult.new(imported: 0, duplicates: 0, errors: ["CSV inválido: #{e.message}"])
  end

  private

  def import_row(row)
    raw_date  = row["Data"]&.strip
    desc      = row["Descrição"]&.strip
    raw_value = row["Valor"]&.strip

    return { error: "Dados incompletos" } if raw_date.blank? || desc.blank? || raw_value.blank?

    value = BankImport::AmountParser.call(raw_value)
    occurred_on = Date.strptime(raw_date, "%d/%m/%Y")

    outcome = BankImport::TransactionWriter.new(@user, account_id: @account_id).write!(
      description: desc,
      amount:      value,
      occurred_on: occurred_on
    )
    return { duplicate: true } if outcome == BankImport::TransactionWriter::DUPLICATE

    { ok: true }
  rescue Date::Error
    { error: "Data inválida: #{row['Data']}" }
  rescue ActiveRecord::RecordInvalid => e
    { error: e.message }
  end
end
