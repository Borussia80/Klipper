require "rails_helper"

RSpec.describe BankImport::RowSigner, type: :service do
  let(:canonical_row) do
    {
      occurred_on: "2026-08-10",
      description: "SUPERMERCADO XYZ",
      amount: "150.00",
      installment_number: nil,
      installment_total: nil
    }
  end

  describe ".sign / .verify!" do
    it "round-trips a signed row back to the original values" do
      token = described_class.sign(canonical_row)

      expect(described_class.verify!(token)).to eq(canonical_row.stringify_keys)
    end

    it "raises InvalidSignature for a tampered token" do
      token = described_class.sign(canonical_row)
      tampered = token[0..-2] + (token[-1] == "a" ? "b" : "a")

      expect { described_class.verify!(tampered) }.to raise_error(BankImport::RowSigner::InvalidSignature)
    end

    it "raises InvalidSignature for a blank token" do
      expect { described_class.verify!(nil) }.to raise_error(BankImport::RowSigner::InvalidSignature)
      expect { described_class.verify!("") }.to raise_error(BankImport::RowSigner::InvalidSignature)
    end

    it "raises InvalidSignature for garbage input" do
      expect { described_class.verify!("not-a-real-token") }.to raise_error(BankImport::RowSigner::InvalidSignature)
    end

    it "verifies successfully within the TTL" do
      token = described_class.sign(canonical_row)

      travel 29.minutes do
        expect(described_class.verify!(token)).to eq(canonical_row.stringify_keys)
      end
    end

    it "raises InvalidSignature once the token has expired" do
      token = described_class.sign(canonical_row)

      travel 31.minutes do
        expect { described_class.verify!(token) }.to raise_error(BankImport::RowSigner::InvalidSignature)
      end
    end

    it "does not verify a token signed for a different purpose" do
      other_token = Rails.application.message_verifier(:something_else).generate(canonical_row.stringify_keys)

      expect { described_class.verify!(other_token) }.to raise_error(BankImport::RowSigner::InvalidSignature)
    end
  end
end
