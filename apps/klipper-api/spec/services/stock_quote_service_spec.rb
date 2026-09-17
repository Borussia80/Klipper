require "rails_helper"

RSpec.describe StockQuoteService, type: :service do
  let(:body) do
    {
      results: [
        { symbol: "PETR4", regularMarketPrice: 38.50, regularMarketChangePercent: 1.23, longName: "Petroleo Brasileiro S.A." }
      ]
    }.to_json
  end

  before do
    Rails.cache.clear
    stub_request(:get, /brapi\.dev/)
      .to_return(status: 200, body: body, headers: { "Content-Type" => "application/json" })
  end

  describe "ticker validation" do
    it "accepts B3 and ADR formats" do
      expect { described_class.fetch([ "PETR4", "BOVA11", "AAPL", "BRK.B" ]) }.not_to raise_error
    end

    it "upcases before validating" do
      described_class.fetch([ "petr4" ])

      expect(a_request(:get, %r{/quote/PETR4\?})).to have_been_made
    end

    it "rejects a ticker carrying extra path segments" do
      expect { described_class.fetch([ "PETR4/../../admin" ]) }
        .to raise_error(described_class::InvalidTicker, /PETR4/)
    end

    it "rejects a ticker carrying extra query parameters" do
      expect { described_class.fetch([ "PETR4?fundamental=true" ]) }
        .to raise_error(described_class::InvalidTicker)
    end

    it "rejects a ticker longer than ten characters" do
      expect { described_class.fetch([ "ABCDEFGHIJK" ]) }.to raise_error(described_class::InvalidTicker)
    end

    it "rejects an empty ticker list" do
      expect { described_class.fetch([]) }.to raise_error(described_class::InvalidTicker, /nenhum ticker/)
    end

    it "makes no outbound request when a ticker is rejected" do
      expect { described_class.fetch([ "PETR4 OR 1=1" ]) }.to raise_error(described_class::InvalidTicker)
      expect(a_request(:get, /brapi\.dev/)).not_to have_been_made
    end
  end

  describe "parsing" do
    it "maps the fields the frontend consumes" do
      quote = described_class.fetch([ "PETR4" ])[:quotes].first

      expect(quote).to eq(
        ticker: "PETR4",
        price: 38.50,
        change_pct: 1.23,
        name: "Petroleo Brasileiro S.A."
      )
    end

    context "when longName is absent" do
      let(:body) { { results: [ { symbol: "PETR4", shortName: "PETROBRAS PN" } ] }.to_json }

      it "falls back to shortName" do
        expect(described_class.fetch([ "PETR4" ])[:quotes].first[:name]).to eq("PETROBRAS PN")
      end
    end

    context "when the price is null" do
      let(:body) { { results: [ { symbol: "PETR4", regularMarketPrice: nil } ] }.to_json }

      it "returns the quote with a nil price instead of raising" do
        quote = described_class.fetch([ "PETR4" ])[:quotes].first

        expect(quote[:ticker]).to eq("PETR4")
        expect(quote[:price]).to be_nil
      end
    end

    context "when the payload has no results key" do
      let(:body) { {}.to_json }

      it "returns an empty quote list" do
        expect(described_class.fetch([ "PETR4" ])[:quotes]).to eq([])
      end
    end

    context "when the body is not JSON" do
      let(:body) { "<html>502 Bad Gateway</html>" }

      it "raises JSON::ParserError for the controller to translate" do
        expect { described_class.fetch([ "PETR4" ]) }.to raise_error(JSON::ParserError)
      end
    end
  end

  describe "caching" do
    it "does not call brapi.dev again for the same ticker set" do
      2.times { described_class.fetch([ "PETR4" ]) }

      expect(a_request(:get, /brapi\.dev/)).to have_been_made.once
    end

    it "calls brapi.dev again for a different ticker set" do
      described_class.fetch([ "PETR4" ])
      described_class.fetch([ "VALE3" ])

      expect(a_request(:get, /brapi\.dev/)).to have_been_made.twice
    end
  end
end
