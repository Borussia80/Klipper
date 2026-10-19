module PdfAdapters
  class SantanderExtratoAdapter < BaseAdapter
    # O PDF real perde espaços entre palavras ("EXTRATODE CONTA"), como os do Itaú.
    STATEMENT_MARKERS = [ /EXTRATO\s*DE\s*CONTA/, /DETALHE\s*DOS\s*MOVIMENTOS/, /Agência:/ ].freeze
    DATE_ROW = /\A(?<date>\d{2}\/\d{2}\/\d{4})\s*(?<description>.*?)\s+(?<amount>-?\s*R\$\s*[\d.]+,\d{2})\s+(?<balance>R\$\s*[\d.]+,\d{2})\z/
    CURRENCY_AMOUNT = /-?\s*R\$\s*[\d.]+,\d{2}/
    DAY_HEADER = /\A(?:segunda|terça|quarta|quinta|sexta|sábado|domingo),\s+\d{2}\s+de\s+/i
    FOOTER = /\A\d+\/\d+\z/
    TABLE_HEADER = /\Adata\s+descrição\s+valor\s+saldo\z/i
    MAX_LINE_LENGTH = 500

    def self.matches?(full_text)
      STATEMENT_MARKERS.all? { |marker| marker.match?(full_text) }
    end

    def parse
      rows = []
      warnings = []
      pending_description = nil
      last_row = nil
      in_details = false
      summary = extract_summary

      @pages.each_with_index do |page, index|
        page.text.each_line do |raw_line|
          line = clean_line(raw_line)
          next if line.empty? || line.length > MAX_LINE_LENGTH

          in_details = true if line.include?("DETALHE DOS MOVIMENTOS")
          next unless in_details
          next if ignored_line?(line)

          if (match = DATE_ROW.match(line))
            row = build_row(match, index + 1, line, pending_description, warnings)
            if row
              rows << row
              last_row = match[:description].strip.blank? ? row : nil
            end
            pending_description = nil
          elsif last_row
            last_row.description = [ last_row.description, line ].reject(&:blank?).join(" ")
            last_row = nil
          else
            pending_description = line
          end
        end
      end

      raise ParseError, "Nenhum lançamento reconhecido no extrato" if rows.empty?

      attach_closing_balance(rows, summary)
      warn_if_summary_does_not_reconcile(summary, warnings)
      ParseResult.new(rows: rows, warnings: warnings)
    end

    private

    def extract_summary
      lines = @pages.flat_map { |page| page.text.each_line.map { |raw_line| clean_line(raw_line) } }
      label_index = lines.index { |line| line.match?(/saldo\s+inicial.*entradas.*saídas.*saldo\s+final/i) }
      return unless label_index

      amounts = lines[(label_index + 1)..].to_a.lazy.map { |line| line.scan(CURRENCY_AMOUNT) }.find { |values| values.size == 4 }
      return unless amounts

      initial, entries, exits, closing = amounts.map { |amount| BankImport::AmountParser.call(amount) }
      { initial: initial, entries: entries, exits: exits, closing: closing, raw_text: amounts.join(" ") }
    end

    # O PDF real usa espaço não separável depois de "R$", que o \s do Ruby não casa.
    def clean_line(raw_line)
      raw_line.tr("\u00A0", " ").strip
    end

    def ignored_line?(line)
      line.include?("DETALHE DOS MOVIMENTOS") || TABLE_HEADER.match?(line) || DAY_HEADER.match?(line) || FOOTER.match?(line)
    end

    def build_row(match, page_number, raw_line, pending_description, warnings)
      occurred_on = Date.strptime(match[:date], "%d/%m/%Y")
      description = match[:description].strip.presence || pending_description

      Row.new(
        occurred_on: occurred_on,
        description: description.to_s,
        amount: BankImport::AmountParser.call(match[:amount]),
        saldo: nil,
        installment_number: nil,
        installment_total: nil,
        page: page_number,
        raw_line: raw_line,
        metadata: { balance: BankImport::AmountParser.call(match[:balance]) }
      )
    rescue ArgumentError
      warnings << Warning.new(page: page_number, raw_text: raw_line, reason: "linha com data não reconhecida")
      nil
    end

    def attach_closing_balance(rows, summary)
      rows.first.metadata[:statement_closing_balance] = summary[:closing] if summary
    end

    def warn_if_summary_does_not_reconcile(summary, warnings)
      return unless summary
      return if summary[:initial] + summary[:entries] - summary[:exits] == summary[:closing]

      warnings << Warning.new(
        page: 1,
        raw_text: summary[:raw_text],
        reason: "saldo inicial + entradas - saídas não confere com saldo final"
      )
    end
  end
end
