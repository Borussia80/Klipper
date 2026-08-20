class CsvImportService
  require "csv"

  ImportResult = Struct.new(:imported, :duplicates, :errors, keyword_init: true)

  DATE_HEADER_ALIASES = %w[data date].freeze
  DESCRIPTION_HEADER_ALIASES = %w[descricao description historico title].freeze
  VALUE_HEADER_ALIASES = %w[valor amount value].freeze
  DATE_FORMATS = [ "%d/%m/%Y", "%Y-%m-%d" ].freeze
  FORMULA_TRIGGER_CHARS = %w[= + - @].freeze

  def initialize(user, file_io, account_id: nil)
    @user = user
    @file_io = file_io
    @account_id = account_id
  end

  def call
    content = @file_io.read
    rows = CSV.parse(content, headers: true, encoding: "UTF-8", col_sep: detect_col_sep(content))
    columns = map_columns(rows.headers)
    unless columns
      return ImportResult.new(imported: 0, duplicates: 0,
                               errors: [ "CSV sem colunas reconhecidas (data/descrição/valor)" ])
    end

    imported = 0
    duplicates = 0
    errors = []

    rows.each_with_index do |row, i|
      result = import_row(row, columns)
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
    ImportResult.new(imported: 0, duplicates: 0, errors: [ "CSV inválido: #{e.message}" ])
  end

  private

  def detect_col_sep(content)
    first_line = content.to_s.each_line.first.to_s
    first_line.count(";") > first_line.count(",") ? ";" : ","
  end

  def map_columns(headers)
    normalized = headers.compact.index_by { |h| normalize_header(h) }
    date_col        = DATE_HEADER_ALIASES.map { |a| normalized[a] }.compact.first
    description_col = DESCRIPTION_HEADER_ALIASES.map { |a| normalized[a] }.compact.first
    value_col       = VALUE_HEADER_ALIASES.map { |a| normalized[a] }.compact.first

    return nil unless date_col && description_col && value_col

    { date: date_col, description: description_col, value: value_col }
  end

  def normalize_header(header)
    header.to_s.strip
          .unicode_normalize(:nfkd)
          .encode("ASCII", invalid: :replace, undef: :replace, replace: "")
          .downcase
  end

  def import_row(row, columns)
    raw_date  = row[columns[:date]]&.strip
    desc      = row[columns[:description]]&.strip
    raw_value = row[columns[:value]]&.strip

    return { error: "Dados incompletos" } if raw_date.blank? || desc.blank? || raw_value.blank?

    value = BankImport::AmountParser.call(raw_value)
    occurred_on = parse_date(raw_date)

    outcome = BankImport::TransactionWriter.new(@user, account_id: @account_id).write!(
      description: sanitize_description(desc),
      amount:      value,
      occurred_on: occurred_on
    )
    return { duplicate: true } if outcome == BankImport::TransactionWriter::DUPLICATE

    { ok: true }
  rescue Date::Error
    { error: "Data inválida: #{raw_date}" }
  rescue ArgumentError
    { error: "Valor inválido: #{raw_value}" }
  rescue ActiveRecord::RecordInvalid, ActiveRecord::RecordNotFound => e
    { error: e.message }
  end

  def parse_date(raw)
    DATE_FORMATS.each do |fmt|
      return Date.strptime(raw, fmt)
    rescue Date::Error
      next
    end
    raise Date::Error, "unrecognized date format"
  end

  def sanitize_description(desc)
    return desc if desc.blank?

    first_char = desc[0]
    FORMULA_TRIGGER_CHARS.include?(first_char) ? "'#{desc}" : desc
  end
end
