# frozen_string_literal: true

class AllowedHosts
  def self.from_env(value)
    value.to_s.split(",").map(&:strip).reject(&:empty?)
  end
end
