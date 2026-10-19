require "rails_helper"

RSpec.describe BusinessCalendar do
  it "calculates Easter" do
    expect(described_class.easter(2026)).to eq(Date.new(2026, 4, 5))
  end

  it "recognizes Good Friday as a non-business day" do
    expect(described_class.business_day?(Date.new(2026, 4, 3))).to be(false)
  end

  it "recognizes Carnival Tuesday as a non-business day" do
    expect(described_class.business_day?(Date.new(2026, 2, 17))).to be(false)
  end

  it "recognizes Black Awareness Day from 2024 onward" do
    expect(described_class.business_day?(Date.new(2026, 11, 20))).to be(false)
  end

  it "does not apply Black Awareness Day before 2024" do
    expect(described_class.business_day?(Date.new(2023, 11, 20))).to be(true)
  end

  it "finds the business day after a Saturday" do
    expect(described_class.next_business_day(Date.new(2026, 11, 14))).to eq(Date.new(2026, 11, 16))
  end

  it "skips Christmas weekend when finding the next business day" do
    expect(described_class.next_business_day(Date.new(2026, 12, 25))).to eq(Date.new(2026, 12, 28))
  end
end
