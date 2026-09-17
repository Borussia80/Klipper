module BankImport
  class AmountParser
    def self.call(raw)
      s = raw.to_s.strip.tr("−", "-")
      return nil if s.blank?

      negative = s.start_with?("-")
      s = s.delete("-").gsub(/[^\d.,]/, "")

      # Com os dois separadores presentes, o da direita é o decimal e o da
      # esquerda é milhar: vale tanto para "1.234,56" (BR) quanto para
      # "1,234.56" (en-US), que antes virava 1.23456 sem levantar erro. Com um
      # separador só o formato é ambíguo ("1.234" pode ser mil ou 1,234) e a
      # convenção BR continua prevalecendo, como antes.
      if s.include?(",") && s.include?(".")
        s = s.rindex(",") > s.rindex(".") ? s.delete(".").sub(",", ".") : s.delete(",")
      elsif s.include?(",")
        s = s.sub(",", ".")
      end

      value = BigDecimal(s)
      negative ? -value : value
    end
  end
end
