module PdfAdapters
  class Registry
    ADAPTERS = [ItauExtratoAdapter, ItauFaturaAdapter].freeze

    def self.detect(full_text)
      ADAPTERS.find { |adapter| adapter.matches?(full_text) }
    end
  end
end
