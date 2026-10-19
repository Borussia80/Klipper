module BankImport
  class OwnTransferMatcher
    TRANSFER_LABEL = /\bpix\s+(?:transf|recebido|enviado)\b|\btransferencia\s+(?:recebida|enviada)\b/.freeze
    INVESTMENT = /\b(?:aplicacao|resgate)\s+rdb\b/.freeze
    NU_PAGAMENTOS_BOLETO = "pagamento de boleto efetuado nu pagamentos sa".freeze

    def self.call(rows, identity:)
      new(rows, identity).call
    end

    def initialize(rows, identity)
      @rows = rows
      @names = identity.names.map { |name| normalize(name) }
      @cpf_mask = identity.cpf_mask.to_s.gsub(/\D/, "")
    end

    def call
      @rows.each { |row| row[:own_transfer] = nil }
      candidates = classify_rows
      pairs = possible_pairs(candidates)
      apply_pairs(candidates, pairs)
      apply_unpaired(candidates)
      @rows
    end

    private

    def classify_rows
      @rows.each_with_index.filter_map do |row, index|
        text = normalize(row[:description])
        if investment?(text)
          row[:own_transfer] = { state: :investment, pair_index: nil }
          next
        end

        next if excluded?(text)

        strength = candidate_strength(text)
        [ index, strength ] if strength
      end
    end

    def possible_pairs(candidates)
      pairs = Hash.new { |hash, key| hash[key] = [] }
      candidates.combination(2) do |left, right|
        next unless left.last == :strong || right.last == :strong
        next unless matching_pair?(left.first, right.first)

        pairs[left.first] << right.first
        pairs[right.first] << left.first
      end
      pairs
    end

    def apply_pairs(candidates, pairs)
      candidates.each do |index, _strength|
        pair_index = pairs[index].first
        next unless pairs[index].one? && pairs[pair_index].one?

        @rows[index][:own_transfer] = { state: :paired, pair_index: }
      end
    end

    def apply_unpaired(candidates)
      candidates.each do |index, strength|
        next if @rows[index][:own_transfer]
        next unless strength == :strong

        @rows[index][:own_transfer] = { state: :to_link, pair_index: nil }
      end
    end

    def candidate_strength(text)
      return :strong if full_name?(text) && (own_cpf_mask?(text) || transfer_label?(text))
      return :prefix if transfer_label?(text) && truncated_name_prefix?(text)
      return :weak if transfer_label?(text) && first_name?(text)

      nil
    end

    # Extratos que imprimem só o primeiro nome, às vezes colado à data
    # ("PIX TRANSF JOSE01/10"). Sozinho não prova nada: só vale pareado com um
    # candidato forte (spec 09, P-2a).
    def first_name?(text)
      @names.any? do |name|
        first = name.split.first
        first && text.match?(/(?<![a-z])#{Regexp.escape(first)}(?![a-z])/)
      end
    end

    def matching_pair?(left_index, right_index)
      left = @rows[left_index]
      right = @rows[right_index]
      left[:account_key] != right[:account_key] &&
        left[:amount].abs == right[:amount].abs &&
        opposite_signs?(left[:amount], right[:amount]) &&
        (left[:occurred_on] - right[:occurred_on]).abs <= 3
    end

    def full_name?(text)
      @names.any? { |name| text.include?(name) }
    end

    def truncated_name_prefix?(text)
      @names.any? do |name|
        prefix = name[0, 15]
        prefix && name.split.size >= 2 && text.include?(prefix)
      end
    end

    def own_cpf_mask?(text)
      return false if @cpf_mask.empty?

      pattern = @cpf_mask.chars.join("[.\\s-]*")
      text.match?(/(?<!\d)#{pattern}(?!\d)/)
    end

    def excluded?(text)
      text.include?("pix devolvido") || text.include?(NU_PAGAMENTOS_BOLETO)
    end

    def investment?(text)
      INVESTMENT.match?(text)
    end

    def transfer_label?(text)
      TRANSFER_LABEL.match?(text)
    end

    def opposite_signs?(left, right)
      (left.negative? && right.positive?) || (left.positive? && right.negative?)
    end

    def normalize(value)
      value.to_s.unicode_normalize(:nfd).gsub(/\p{Mn}/, "").downcase.gsub(/[^\p{Alnum}]+/, " ").strip
    end
  end
end
