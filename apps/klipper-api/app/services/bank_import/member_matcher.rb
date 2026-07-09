module BankImport
  class MemberMatcher
    CARDHOLDER_SUFFIX = /\s*\(final\s*\d+\)\z/i

    def self.normalize(str)
      return "" if str.blank?
      str.to_s.unicode_normalize(:nfkd)
         .encode("ASCII", replace: "", invalid: :replace, undef: :replace)
         .upcase.gsub(/[^A-Z0-9]/, "")
    end

    def self.match(cardholder, members)
      return nil if cardholder.blank?
      normalized_cardholder = normalize(cardholder.to_s.sub(CARDHOLDER_SUFFIX, ""))
      return nil if normalized_cardholder.blank?

      members.find do |m|
        normalized = normalize(m.name)
        normalized.present? &&
          (normalized_cardholder == normalized || normalized_cardholder.include?(normalized))
      end
    end
  end
end
