module PdfAdapters
  # Fatura Itaú: layout de 2 colunas (um cartão adicional por coluna) dentro da seção
  # "Lançamentos: compras e saques". pdf-reader's page.text concatena as duas colunas na
  # mesma linha de texto (colunas coladas), então NÃO dá pra usar regex linha-a-linha como
  # no ItauExtratoAdapter — precisamos de dados posicionais (x/y de cada run) via
  # `PDF::Reader::Page#runs` pra reconstruir cada coluna separadamente.
  #
  # Confirmado na fixture real: coluna esquerda em x < COLUMN_SPLIT_X, direita em x >=.
  # As datas nas faturas não têm ano (ex. "21/06") — o ano é inferido a partir da data de
  # emissão da fatura (linha "Emissão: DD/MM/AAAA" no topo), assumindo que meses maiores que
  # o mês de emissão pertencem ao ano anterior (compra antiga sendo cobrada faseada).
  class ItauFaturaAdapter < BaseAdapter
    COLUMN_SPLIT_X = 350

    TRANSACTION_ROW = /\A(\d{2})\/(\d{2})\s+(.+?)\s+(-?[\d.]+,\d{2})\z/
    CARDHOLDER_ROW = /\A(.+?)\(final\s*(\d{3,6})\)\z/i
    PRINCIPAL_JUROS = /principal\s*\(r\$\s*([\d.,]+)\s*\)\s*\+\s*juros\s*\(r\$\s*([\d.,]+)\s*\)/i
    CONVERSION_RATE_LINE = /d.{0,2}lar\s*de\s*convers/i
    CATEGORY_CITY_LINE = /\A[^.]+\s\.\s*\S/
    EMISSAO_LINE = /emiss.{0,2}:\s*(\d{2})\/(\d{2})\/(\d{4})/i

    def self.matches?(full_text)
      !!(full_text =~ /resumodafatura|lan\w*mentos:?compras\w*saques/i)
    end

    def parse
      full_text = @pages.map(&:text).join("\n")
      @emission_date = extract_emission_date(full_text)
      @section = :none
      @cardholder = { left: nil, right: nil }
      @last_row = { left: nil, right: nil }

      rows = []
      warnings = []

      @pages.each_with_index do |page, index|
        page_number = index + 1

        group_runs_into_rows(page.runs).each do |left_text, right_text|
          process_cell(left_text, :left, page_number, rows)
          process_cell(right_text, :right, page_number, rows) if @section == :compras_saques
        end
      end

      raise ParseError, "Nenhum lançamento reconhecido na fatura" if rows.empty?

      ParseResult.new(rows: rows, warnings: warnings)
    end

    private

    def group_runs_into_rows(runs)
      grouped = runs.group_by { |r| r.y.round }
      grouped.sort_by { |y_key, _| -y_key }.map do |_, row_runs|
        left = row_runs.select { |r| r.x < COLUMN_SPLIT_X }.sort_by(&:x)
        right = row_runs.select { |r| r.x >= COLUMN_SPLIT_X }.sort_by(&:x)
        [ left.map(&:text).join(" ").strip, right.map(&:text).join(" ").strip ]
      end
    end

    def process_cell(text, side, page_number, rows)
      return if text.blank?

      norm = text.gsub(/\s+/, "").downcase

      if (new_section = detect_section(norm))
        if new_section != @section
          @section = new_section
          @cardholder[:left] = nil
          @cardholder[:right] = nil
        end
        return
      end

      return if @section == :none || @section == :proximas_faturas

      if (m = CARDHOLDER_ROW.match(text))
        @cardholder[side] = "#{m[1].strip} (final #{m[2]})"
        return
      end

      if (m = TRANSACTION_ROW.match(text))
        day, month, description_and_installment, amount_str = m.captures
        description, installment_number, installment_total = split_installment(description_and_installment)

        metadata = { section: @section.to_s }
        metadata[:cardholder] = @cardholder[side] if @cardholder[side]

        row = Row.new(
          occurred_on: build_date(day, month),
          description: description,
          # Convenção do app: amount negativo = débito/despesa, positivo = crédito/entrada
          # (mesma convenção do extrato e do CSV). Numa fatura de cartão é o oposto do que é
          # impresso: um valor positivo é uma compra (despesa), um negativo é estorno/crédito.
          amount: -BankImport::AmountParser.call(amount_str),
          saldo: nil,
          installment_number: installment_number,
          installment_total: installment_total,
          page: page_number,
          raw_line: text,
          metadata: metadata
        )
        rows << row
        @last_row[side] = row
        return
      end

      # linhas de subtotal/total por cartão ou por seção (ex. "Lançamentos no cartão (final
      # XXXX) 2.037,40", "Total lançamentos inter. em R$ ...") nunca são lançamentos.
      return if norm.start_with?("lan") || norm.start_with?("total") || norm.include?("repassedeiof")

      if @section == :produtos_servicos && (m = PRINCIPAL_JUROS.match(text))
        attach_metadata(side, principal: BankImport::AmountParser.call(m[1]), juros: BankImport::AmountParser.call(m[2]))
        return
      end

      if @section == :internacional
        return if CONVERSION_RATE_LINE.match?(text)

        currency = text[/\b(?!BRL\b)([A-Z]{3})\b/, 1]
        attach_metadata(side, original_currency: currency, detail: text) if @last_row[side]
        return
      end

      nil if CATEGORY_CITY_LINE.match?(text) # linha de categoria/cidade da seção compras e saques - só informativa
    end

    def attach_metadata(side, **fields)
      row = @last_row[side]
      return unless row

      fields.each { |k, v| row.metadata[k] = v if v }
    end

    def detect_section(norm)
      return :proximas_faturas if norm.include?("comprasparceladas") && norm =~ /pr.{0,2}ximasfaturas/
      return :compras_saques if norm.start_with?("lan") && norm.include?("comprasesaques")
      return :internacional if norm.start_with?("lan") && norm.include?("internacion")
      return :produtos_servicos if norm.start_with?("lan") && norm.include?(":produtoseservi")

      nil
    end

    def split_installment(blob)
      # A sufixo "DD/DD" de parcela às vezes vem colado ao nome do estabelecimento sem
      # espaço (mesmo problema de concatenação do pdf-reader), por isso \s* e não \s+.
      if (m = /\A(.+?)\s*(\d{2})\/(\d{2})\z/.match(blob))
        [ m[1].strip, m[2].to_i, m[3].to_i ]
      else
        [ blob.strip, nil, nil ]
      end
    end

    def build_date(day, month)
      month_i = month.to_i
      year = @emission_date.year
      year -= 1 if month_i > @emission_date.month
      Date.new(year, month_i, day.to_i)
    end

    def extract_emission_date(full_text)
      match = EMISSAO_LINE.match(full_text)
      raise ParseError, "Não foi possível localizar a data de emissão da fatura" unless match

      Date.new(match[3].to_i, match[2].to_i, match[1].to_i)
    end
  end
end
