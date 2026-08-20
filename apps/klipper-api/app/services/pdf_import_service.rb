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
    suggestions = cardholder_suggestions(result.rows)
    PreviewResult.new(
      adapter: adapter_class.adapter_key,
      rows: result.rows.map { |row| serialize_row(row, suggestions) },
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
    signed = BankImport::RowSigner.verify!(row[:token])

    BankImport::TransactionWriter.new(@user, account_id: @account_id).write!(
      description: signed[:description],
      amount: BigDecimal(signed[:amount].to_s),
      occurred_on: Date.parse(signed[:occurred_on].to_s),
      installment_number: signed[:installment_number].presence,
      installment_total: signed[:installment_total].presence,
      member_id: row[:member_id].presence
    )
  end

  def cardholder_suggestions(rows)
    members = @user.members.active.to_a
    rows.filter_map { |r| r.metadata[:cardholder] }.uniq.index_with do |cardholder|
      BankImport::MemberMatcher.match(cardholder, members)&.id
    end
  end

  # member_id fica de fora do canonical (RowSigner/SEC-17) de propósito: os outros 5 campos são
  # fato financeiro que tem que rastrear ao PDF original, mas member_id é sugestão editável — o
  # usuário corrige o portador auto-detectado antes de confirmar (ver ModalConfirmarImportacao/
  # importar.vue:264, seleção por grupo de titular). Assinar member_id travaria essa correção no
  # valor sugerido no preview. O risco real (member_id de outro usuário) já é bloqueado em
  # BankImport::TransactionWriter#write! (validação de posse contra @user.members, SEC-05).
  def serialize_row(row, suggestions = {})
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
      token: BankImport::RowSigner.sign(canonical)
    )
  end

  def serialize_warning(warning)
    { page: warning.page, reason: warning.reason }
  end
end
