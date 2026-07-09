module PdfAdapters
  class ParseError < StandardError; end

  Row = Struct.new(
    :occurred_on, :description, :amount, :saldo,
    :installment_number, :installment_total,
    :page, :raw_line, :metadata,
    keyword_init: true
  )

  Warning = Struct.new(:page, :raw_text, :reason, keyword_init: true)

  ParseResult = Struct.new(:rows, :warnings, keyword_init: true)

  class BaseAdapter
    def self.matches?(full_text)
      raise NotImplementedError
    end

    def self.adapter_key
      name.demodulize.underscore.sub(/_adapter$/, "")
    end

    def initialize(pages)
      @pages = pages
    end

    def parse
      raise NotImplementedError
    end
  end
end
