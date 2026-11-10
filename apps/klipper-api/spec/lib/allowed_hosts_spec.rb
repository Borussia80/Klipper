require "spec_helper"
require_relative "../../lib/allowed_hosts"

RSpec.describe AllowedHosts do
  describe ".from_env" do
    it "parses the comma-separated production host allowlist" do
      expect(described_class.from_env("klipper-api.onrender.com, api.klipper.app")).to eq(
        [ "klipper-api.onrender.com", "api.klipper.app" ]
      )
    end

    it "allows the forwarded frontend host with the production host allowlist" do
      hosts = described_class.from_env("klipper-api.onrender.com,klipper.quebec.com.br,www.klipper.quebec.com.br,klipper-app.vercel.app")

      expect(hosts).to include("klipper.quebec.com.br", "www.klipper.quebec.com.br", "klipper-app.vercel.app")
    end

    it "ignores blank entries" do
      expect(described_class.from_env(" klipper-api.onrender.com, ,\t")).to eq([ "klipper-api.onrender.com" ])
    end

    it "returns an empty allowlist when the env var is unset" do
      expect(described_class.from_env(nil)).to eq([])
    end
  end
end
