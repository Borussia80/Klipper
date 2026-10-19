class CsvImportService
  require "csv"

  ImportResult = Struct.new(:imported, :duplicates, :errors, keyword_init: true)
  PreviewResult = Struct.new(:adapter, :rows, :warnings, :error, keyword_init: true) do
    def error?
      error.present?
    end
  end
  PreviewRow = Struct.new(:occurred_on, :description, :amount, :page, :metadata,
                          :installment_number, :installment_total, keyword_init: true)

  DATE_HEADER_ALIASES = %w[data date].freeze
  DESCRIPTION_HEADER_ALIASES = %w[descricao description historico title].freeze
  VALUE_HEADER_ALIASES = %w[valor amount value].freeze
  DATE_FORMATS = [ "%d/%m/%Y", "%Y-%m-%d" ].freeze
  FORMULA_TRIGGER_CHARS = %w[= + - @].freeze
  IncompleteRowError = Class.new(StandardError)

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
    ordinals = Hash.new(0)

    rows.each_with_index do |row, i|
      result = import_row(row, columns, ordinals)
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

  def preview
    content = @file_io.read
    rows = CSV.parse(content, headers: true, encoding: "UTF-8", col_sep: detect_col_sep(content))
    columns = map_columns(rows.headers)
    return PreviewResult.new(rows: [], warnings: [], error: "CSV sem colunas reconhecidas (data/descrição/valor)") unless columns

    preview_rows = []
    warnings = []
    rows.each_with_index do |row, index|
      preview_row = build_preview_row(row, columns, index + 2)
      if preview_row[:error]
        warnings << { page: index + 2, reason: preview_row[:error] }
      else
        preview_rows << preview_row[:row]
      end
    end

    PreviewResult.new(
      adapter: "csv",
      rows: BankImport::PreviewSerializer.new(@user, account_id: @account_id).serialize(preview_rows),
      warnings:
    )
  rescue CSV::MalformedCSVError => e
    PreviewResult.new(rows: [], warnings: [], error: "CSV inválido: #{e.message}")
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

  def import_row(row, columns, ordinals)
    attributes = row_attributes(row, columns)

    outcome = BankImport::TransactionWriter.new(@user, account_id: @account_id, ordinals: ordinals).write!(
      **attributes
    )
    return { duplicate: true } if outcome == BankImport::TransactionWriter::DUPLICATE

    { ok: true }
  rescue IncompleteRowError
    { error: "Dados incompletos" }
  rescue Date::Error
    { error: "Data inválida: #{raw_date(row, columns)}" }
  rescue ArgumentError
    { error: "Valor inválido: #{raw_value(row, columns)}" }
  rescue ActiveRecord::RecordInvalid, ActiveRecord::RecordNotFound => e
    { error: e.message }
  end

  def build_preview_row(row, columns, line_number)
    attributes = row_attributes(row, columns)
    { row: PreviewRow.new(**attributes, page: line_number, metadata: {}, installment_number: nil, installment_total: nil) }
  rescue IncompleteRowError
    { error: "Dados incompletos" }
  rescue Date::Error
    { error: "Data inválida: #{raw_date(row, columns)}" }
  rescue ArgumentError
    { error: "Valor inválido: #{raw_value(row, columns)}" }
  end

  def row_attributes(row, columns)
    raw_date = raw_date(row, columns)
    desc = row[columns[:description]]&.strip
    raw_value = raw_value(row, columns)
    raise IncompleteRowError if raw_date.blank? || desc.blank? || raw_value.blank?

    { description: sanitize_description(desc), amount: BankImport::AmountParser.call(raw_value), occurred_on: parse_date(raw_date) }
  end

  def raw_date(row, columns)
    row[columns[:date]]&.strip
  end

  def raw_value(row, columns)
    row[columns[:value]]&.strip
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
