module BankImport
  class DescriptionNormalizer
    AUTHORIZATION_NUMBER = /\b(?:nsu|aut|autorizacao)\b\s*:?\s*\d+\b/

    def self.call(text)
      I18n.transliterate(text.to_s).downcase
        .gsub(AUTHORIZATION_NUMBER, " ")
        .squish
    end
  end
end
