require "pdf/reader"

# Orquestra o fluxo preview -> confirm de importação de PDF (extrato/fatura Itaú).
# Diferente do CsvImportService, nunca persiste no #preview: só extrai e devolve as linhas
# para o cliente revisar/desmarcar. O #confirm recebe de volta exatamente o array de rows
# que o #preview devolveu (o cliente pode ter removido linhas desmarcadas pelo usuário).
class PdfImportService
  PreviewResult = Struct.new(:adapter, :rows, :warnings, :error, keyword_init: true) do
    def error?
      error.present?
    end
  end

  ImportResult = Struct.new(:imported, :duplicates, :errors, keyword_init: true)

  def initialize(user, account_id: nil)
    @user = user
    @account_id = account_id
  end

  def preview(file_io)
    io = file_io.is_a?(IO) || file_io.is_a?(StringIO) || file_io.is_a?(Tempfile) ? file_io : file_io.path
    pages = PDF::Reader.new(io).pages
    full_text = pages.map(&:text).join("\n")

    adapter_class = PdfAdapters::Registry.detect(full_text)
    return PreviewResult.new(rows: [], warnings: [], error: "Layout de PDF não reconhecido") unless adapter_class

    result = adapter_class.new(pages).parse
    suggestions = cardholder_suggestions(result.rows)
    PreviewResult.new(
      adapter: adapter_class.adapter_key,
      rows: result.rows.map { |row| serialize_row(row, suggestions) },
      warnings: result.warnings.map { |warning| serialize_warning(warning) }
    )
  rescue PDF::Reader::MalformedPDFError
    PreviewResult.new(rows: [], warnings: [], error: "PDF corrompido ou ilegível")
  rescue PdfAdapters::ParseError => e
    PreviewResult.new(rows: [], warnings: [], error: e.message)
  end

  def confirm(rows)
    imported = 0
    duplicates = 0
    errors = []

    Array(rows).each_with_index do |row, index|
      outcome = import_row(row)
      if outcome == BankImport::TransactionWriter::DUPLICATE
        duplicates += 1
      else
        imported += 1
      end
    rescue => e
      errors << "Linha #{index + 1}: #{e.message}"
    end

    ImportResult.new(imported: imported, duplicates: duplicates, errors: errors)
  end

  private

  def import_row(row)
    row = row.with_indifferent_access

    BankImport::TransactionWriter.new(@user, account_id: @account_id).write!(
      description: row[:description],
      amount: BigDecimal(row[:amount].to_s),
      occurred_on: Date.parse(row[:occurred_on].to_s),
      installment_number: row[:installment_number].presence,
      installment_total: row[:installment_total].presence,
      member_id: row[:member_id].presence
    )
  end

  def cardholder_suggestions(rows)
    members = @user.members.active.to_a
    rows.filter_map { |r| r.metadata[:cardholder] }.uniq.index_with do |cardholder|
      BankImport::MemberMatcher.match(cardholder, members)&.id
    end
  end

  def serialize_row(row, suggestions = {})
    {
      occurred_on: row.occurred_on.iso8601,
      description: row.description,
      amount: row.amount.to_s("F"),
      installment_number: row.installment_number,
      installment_total: row.installment_total,
      page: row.page,
      metadata: row.metadata,
      suggested_member_id: suggestions[row.metadata[:cardholder]]
    }
  end

  def serialize_warning(warning)
    { page: warning.page, reason: warning.reason }
  end
end
