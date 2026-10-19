require "bigdecimal"

module Money
  module_function

  def round(value)
    value.round(2, BigDecimal::ROUND_HALF_EVEN)
  end

  def split(total, count, remainder: :first)
    raise ArgumentError, "count must be at least one" if count < 1

    total_cents = (total * 100).to_i
    raise ArgumentError, "total must be at least one cent per part" if total_cents < count

    base_cents, extra_cents = total_cents.divmod(count)
    parts = Array.new(count, BigDecimal(base_cents.to_s) / 100)
    remainder_index = remainder == :last ? -1 : 0

    parts[remainder_index] += BigDecimal(extra_cents.to_s) / 100
    parts
  end
end
