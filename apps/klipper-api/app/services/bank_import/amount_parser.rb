module BankImport
  class AmountParser
    def self.call(raw)
      s = raw.to_s.strip.tr("−", "-")
      return nil if s.blank?

      negative = s.start_with?("-")
      s = s.delete("-").gsub(/[^\d.,]/, "")
      s = s.delete(".").sub(",", ".") if s.include?(",")

      value = BigDecimal(s)
      negative ? -value : value
    end
  end
end
