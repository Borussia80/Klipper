require "rails_helper"

RSpec.describe Money do
  describe ".split" do
    it "puts the remainder in the first part" do
      expect(described_class.split(BigDecimal("100.00"), 3, remainder: :first)).to eq(
        [ BigDecimal("33.34"), BigDecimal("33.33"), BigDecimal("33.33") ]
      )
    end

    it "splits one thousand reais into seven installments" do
      expect(described_class.split(BigDecimal("1000.00"), 7, remainder: :first)).to eq(
        [ BigDecimal("142.90") ] + Array.new(6, BigDecimal("142.85"))
      )
    end

    it "puts the remainder in the last part" do
      expect(described_class.split(BigDecimal("100.00"), 3, remainder: :last)).to eq(
        [ BigDecimal("33.33"), BigDecimal("33.33"), BigDecimal("33.34") ]
      )
    end

    it "rejects a split that would create zero-value parts" do
      expect { described_class.split(BigDecimal("0.01"), 3) }.to raise_error(ArgumentError)
    end

    it "always preserves the total for 200 random values" do
      random = Random.new(12_345)

      200.times do
        count = random.rand(1..48)
        total = BigDecimal(random.rand(count..1_000_000).to_s) / 100

        expect(described_class.split(total, count).sum).to eq(total)
      end
    end
  end

  describe ".round" do
    it "rounds a half cent down when the retained digit is even" do
      expect(described_class.round(BigDecimal("2.345"))).to eq(BigDecimal("2.34"))
    end

    it "rounds a half cent up when the retained digit is odd" do
      expect(described_class.round(BigDecimal("2.355"))).to eq(BigDecimal("2.36"))
    end

    it "rounds only the final result of a calculation" do
      amount = BigDecimal("1234.56") * BigDecimal("0.0199")

      expect(described_class.round(amount)).to eq(BigDecimal("24.57"))
    end
  end
end
