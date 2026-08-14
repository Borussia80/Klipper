module PdfAdapters
  # Fatura Nubank: layout de coluna única (diferente da fatura Itaú Personnalite, que usa
  # 2 colunas para cartões adicionais). pdf-reader preserva o espaçamento entre palavras
  # nesse PDF (ao contrário do extrato Itaú), então dá pra usar regex linha-a-linha direto
  # em page.text, sem precisar de dados posicionais (runs).
  #
  # Datas de lançamento não têm ano (ex. "19 JUN") — o ano é inferido a partir da data de
  # emissão da fatura (linha "EMISSÃO E ENVIO DD MON AAAA" no cabeçalho), com a mesma regra
  # da fatura Itaú: mês do lançamento maior que o mês de emissão => ano anterior.
  #
  # O parsing só processa linhas dentro da seção "TRANSAÇÕES DE ... A ..." — sem esse filtro,
  # linhas de resumo nas páginas anteriores (ex. "Pagamento mínimo ... R$ 23,95") também
  # combinam com o padrão de cabeçalho/subtotal e corrompem o titular rastreado.
  #
  # Confirmado apenas contra 1 fatura real (titular único, sem cartão adicional, sem parcela):
  # "Pagamentos" é o único rótulo de seção sem titular observado até agora. Se aparecerem
  # outras seções administrativas (IOF, encargos, estornos) ou parcelamento num PDF real
  # futuro, ajustar aqui com evidência — não estender por suposição.
  class NubankFaturaAdapter < BaseAdapter
    MONTHS = {
      "JAN" => 1, "FEV" => 2, "MAR" => 3, "ABR" => 4, "MAI" => 5, "JUN" => 6,
      "JUL" => 7, "AGO" => 8, "SET" => 9, "OUT" => 10, "NOV" => 11, "DEZ" => 12
    }.freeze

    EMISSAO_LINE = /EMISS.{1,3}O\s+E\s+ENVIO\s+(\d{2})\s+([A-ZÇ]{3})\s+(\d{4})/i
    TRANSACOES_HEADER = /\ATRANSA.{1,3}ES\s+DE\s+\d{2}\s+[A-ZÇ]{3}\s+A\s+\d{2}\s+[A-ZÇ]{3}/i
    TRANSACTION_ROW = /\A(\d{2})\s+([A-ZÇ]{3})\s+(?:[••]+\s*(\d{3,4})\s+)?(.+?)\s+((?:-|−)?R\$\s?[\d.,]+)\z/i
    HEADER_ROW = /\A([A-ZÀ-Úa-zà-ú][\wÀ-ÿ .]*?)\s+((?:-|−)?R\$\s?[\d.,]+)\z/
    NON_CARDHOLDER_HEADERS = [ "pagamentos" ].freeze

    def self.matches?(full_text)
      !!(full_text =~ /nubank/i && full_text =~ /RESUMO\s+DA\s+FATURA/i)
    end

    def parse
      full_text = @pages.map(&:text).join("\n")
      @emission_date = extract_emission_date(full_text)
      @cardholder = nil
      @in_transactions = false

      rows = []
      warnings = []

      @pages.each_with_index do |page, index|
        page_number = index + 1

        page.text.each_line do |raw_line|
          line = raw_line.strip
          next if line.empty?

          @in_transactions = true if TRANSACOES_HEADER.match?(line)
          next unless @in_transactions

          if (match = TRANSACTION_ROW.match(line))
            rows << build_row(match, page_number, line)
          elsif (match = HEADER_ROW.match(line))
            @cardholder = NON_CARDHOLDER_HEADERS.include?(match[1].strip.downcase) ? nil : match[1].strip
          end
        end
      end

      raise ParseError, "Nenhum lançamento reconhecido na fatura" if rows.empty?

      ParseResult.new(rows: rows, warnings: warnings)
    end

    private

    def build_row(match, page_number, raw_line)
      day, month_abbr, card_last4, description, amount_str = match.captures
      metadata = {}
      metadata[:cardholder] = @cardholder if @cardholder
      metadata[:card_last4] = card_last4 if card_last4

      Row.new(
        occurred_on: build_date(day, month_abbr),
        description: description.strip,
        # Convenção do app: negativo = débito/despesa, positivo = crédito/entrada.
        # Na fatura Nubank é o oposto do que é impresso: uma compra aparece positiva,
        # um pagamento/estorno aparece negativo.
        amount: -BankImport::AmountParser.call(amount_str),
        saldo: nil,
        installment_number: nil,
        installment_total: nil,
        page: page_number,
        raw_line: raw_line,
        metadata: metadata
      )
    end

    def build_date(day, month_abbr)
      month_i = month_number(month_abbr)
      year = @emission_date.year
      year -= 1 if month_i > @emission_date.month
      Date.new(year, month_i, day.to_i)
    end

    def extract_emission_date(full_text)
      match = EMISSAO_LINE.match(full_text)
      raise ParseError, "Não foi possível localizar data de emissão da fatura" unless match

      day, month_abbr, year = match.captures
      Date.new(year.to_i, month_number(month_abbr), day.to_i)
    end

    def month_number(abbr)
      MONTHS.fetch(abbr.upcase) { raise ParseError, "Mês não reconhecido: #{abbr}" }
    end
  end
end
