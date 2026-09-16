require "rails_helper"

RSpec.describe JwtService do
  describe ".encode" do
    it "carries the payload claims through" do
      decoded = described_class.decode(described_class.encode(user_id: 42, token_version: 3))

      expect(decoded[:user_id]).to eq(42)
      expect(decoded[:token_version]).to eq(3)
    end

    it "stamps the token as an access token" do
      expect(described_class.decode(described_class.encode(user_id: 1))[:token_type]).to eq("access")
    end

    it "expires in 15 minutes" do
      freeze_time do
        decoded = described_class.decode(described_class.encode(user_id: 1))
        expect(decoded[:exp]).to eq(described_class::ACCESS_EXPIRY.from_now.to_i)
      end
    end
  end

  describe ".encode_refresh" do
    it "stamps the token as a refresh token" do
      decoded = described_class.decode(described_class.encode_refresh(user_id: 1))
      expect(decoded[:token_type]).to eq("refresh")
    end

    it "expires in 30 days" do
      freeze_time do
        decoded = described_class.decode(described_class.encode_refresh(user_id: 1))
        expect(decoded[:exp]).to eq(described_class::REFRESH_EXPIRY.from_now.to_i)
      end
    end

    # O par access/refresh só é separável porque os dois tipos são distinguíveis
    # no payload. É desta distinção que o portão do BaseController depende.
    it "is distinguishable from an access token with the same payload" do
      payload = { user_id: 1, token_version: 0 }

      access = described_class.decode(described_class.encode(payload))
      refresh = described_class.decode(described_class.encode_refresh(payload))

      expect(access[:token_type]).not_to eq(refresh[:token_type])
    end
  end

  describe ".decode" do
    it "returns nil for a blank token" do
      expect(described_class.decode(nil)).to be_nil
      expect(described_class.decode("")).to be_nil
    end

    it "returns nil for a malformed token" do
      expect(described_class.decode("not-a-jwt")).to be_nil
    end

    it "returns nil when the signature does not match" do
      foreign = JWT.encode({ user_id: 1, exp: 1.hour.from_now.to_i }, "outra-chave", "HS256")
      expect(described_class.decode(foreign)).to be_nil
    end

    it "returns nil for an expired token" do
      token = described_class.encode(user_id: 1)
      travel(described_class::ACCESS_EXPIRY + 1.minute) do
        expect(described_class.decode(token)).to be_nil
      end
    end

    it "reads claims by string or symbol" do
      decoded = described_class.decode(described_class.encode(user_id: 7))

      expect(decoded[:user_id]).to eq(7)
      expect(decoded["user_id"]).to eq(7)
    end
  end
end
