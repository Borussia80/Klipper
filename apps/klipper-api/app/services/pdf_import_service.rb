require "pdf/reader"
require "timeout"

# Orquestra o fluxo preview -> confirm de importação de PDF (extrato/fatura Itaú).
# Diferente do CsvImportService, nunca persiste no #preview: só extrai e devolve as linhas
# para o cliente revisar/desmarcar. O #confirm recebe de volta exatamente o array de rows
# que o #preview devolveu (o cliente pode ter removido linhas desmarcadas pelo usuário).
class PdfImportService
  MAX_PDF_PAGES = 500
  PDF_READ_TIMEOUT = 30

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
    pages = Timeout.timeout(PDF_READ_TIMEOUT) { PDF::Reader.new(io).pages }

    return PreviewResult.new(rows: [], warnings: [],
                             error: "PDF excede limite de #{MAX_PDF_PAGES} páginas") if pages.size > MAX_PDF_PAGES

    full_text = pages[0, MAX_PDF_PAGES].map(&:text).join("\n")

    adapter_class = PdfAdapters::Registry.detect(full_text)
    return PreviewResult.new(rows: [], warnings: [], error: "Layout de PDF não reconhecido") unless adapter_class

    result = adapter_class.new(pages).parse
    PreviewResult.new(
      adapter: adapter_class.adapter_key,
      rows: BankImport::PreviewSerializer.new(@user, account_id: @account_id).serialize(result.rows),
      warnings: result.warnings.map { |warning| serialize_warning(warning) }
    )
  rescue Timeout::Error
    PreviewResult.new(rows: [], warnings: [], error: "Tempo limite de leitura do PDF excedido")
  rescue PDF::Reader::MalformedPDFError
    PreviewResult.new(rows: [], warnings: [], error: "PDF corrompido ou ilegível")
  rescue PdfAdapters::ParseError => e
    PreviewResult.new(rows: [], warnings: [], error: e.message)
  rescue Date::Error, ArgumentError => e
    PreviewResult.new(rows: [], warnings: [], error: "Não foi possível interpretar o extrato: #{e.message}")
  end

  def confirm(rows)
    imported = 0
    duplicates = 0
    errors = []
    ordinals = Hash.new(0)

    Array(rows).each_with_index do |row, index|
      outcome = import_row(row, ordinals)
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

  def import_row(row, ordinals)
    row = row.with_indifferent_access
    signed = BankImport::RowSigner.verify!(row[:token])

    BankImport::TransactionWriter.new(@user, account_id: @account_id, ordinals: ordinals).write!(
      description: signed[:description],
      amount: BigDecimal(signed[:amount].to_s),
      occurred_on: Date.parse(signed[:occurred_on].to_s),
      installment_number: signed[:installment_number].presence,
      installment_total: signed[:installment_total].presence,
      member_id: row[:member_id].presence,
      kind: row[:kind] == "transfer" ? "transfer" : nil
    )
  end

  def serialize_warning(warning)
    { page: warning.page, reason: warning.reason }
  end
end
