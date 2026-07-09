require "rails_helper"

RSpec.describe BankImport::MemberMatcher, type: :service do
  let(:user) { create(:user) }
  let(:clarea) { create(:member, user: user, name: "Clarea Ana Almeida") }
  let(:jose)   { create(:member, user: user, name: "José da Silva") }
  let(:members) { [ clarea, jose ] }

  describe ".match" do
    it "matches an exact normalized name" do
      expect(described_class.match("CLAREAANAALMEIDA (final 7445)", members)).to eq(clarea)
    end

    it "matches when the cardholder name contains the member's normalized name" do
      expect(described_class.match("CLAREAANAALMEIDAJUNIOR (final 1234)", members)).to eq(clarea)
    end

    it "is accent-insensitive" do
      expect(described_class.match("JOSEDASILVA (final 9999)", members)).to eq(jose)
    end

    it "returns nil when the cardholder is blank" do
      expect(described_class.match("", members)).to be_nil
      expect(described_class.match(nil, members)).to be_nil
    end

    it "returns nil when there is no match" do
      expect(described_class.match("FULANODETAL (final 0001)", members)).to be_nil
    end
  end

  describe ".normalize" do
    it "upcases, strips accents and removes non-alphanumeric characters" do
      expect(described_class.normalize("José da Silva")).to eq("JOSEDASILVA")
    end

    it "returns an empty string for blank input" do
      expect(described_class.normalize(nil)).to eq("")
      expect(described_class.normalize("")).to eq("")
    end
  end
end
