module PdfAdapters
  class ItauExtratoAdapter < BaseAdapter
    # pdf-reader's page.text não preserva espaçamento interno de palavras dentro de blocos de
    # texto (diferente do pdftotext -layout usado na análise manual original): a descrição
    # chega como um blob colado, ex. "PIXTRANSFJOAOPA31/12" em vez de "PIX TRANSF JOAO PA 31/12".
    # Datas e valores continuam bem delimitados por espaço. Por isso o regex de linha e a
    # exclusão de "SALDO DO DIA" são tolerantes a texto sem espaços internos.
    ROW_REGEX = /\A(\d{2}\/\d{2}\/\d{4})\s+(.+?)\s+(-?[\d.]+,\d{2})\z/
    SALDO_DIA_NORMALIZED = "saldododia".freeze
    MAX_LINE_LENGTH = 300

    def self.matches?(full_text)
      !!(full_text =~ /agência:\d+conta:/i)
    end

    def parse
      rows = []
      warnings = []

      @pages.each_with_index do |page, index|
        page_number = index + 1

        page.text.each_line do |raw_line|
          line = raw_line.strip
          next if line.empty?
          next if line.length > MAX_LINE_LENGTH

          match = ROW_REGEX.match(line)
          unless match
            if line =~ /\A\d{2}\/\d{2}\/\d{4}/
              warnings << Warning.new(page: page_number, raw_text: line, reason: "linha com data não reconhecida")
            end
            next
          end

          date_str, description, amount_str = match.captures
          next if description.gsub(/\s+/, "").downcase == SALDO_DIA_NORMALIZED

          rows << Row.new(
            occurred_on: Date.strptime(date_str, "%d/%m/%Y"),
            description: clean_description(description, date_str),
            amount: BankImport::AmountParser.call(amount_str),
            saldo: nil,
            installment_number: nil,
            installment_total: nil,
            page: page_number,
            raw_line: line,
            metadata: {}
          )
        end
      end

      raise ParseError, "Nenhum lançamento reconhecido no extrato" if rows.empty?

      ParseResult.new(rows: rows, warnings: warnings)
    end

    private

    # Itaú costuma repetir "DD/MM" da própria data do lançamento colado ao fim da descrição
    # (ex. "PIXTRANSFJOAOPA31/12" quando a data é 31/12/2025). Remove essa repetição quando
    # presente, sem inventar espaçamento que a extração não tem.
    def clean_description(description, date_str)
      day_month_suffix = "#{date_str[0, 2]}/#{date_str[3, 2]}"
      description.delete_suffix(day_month_suffix).strip
    end
  end
end
