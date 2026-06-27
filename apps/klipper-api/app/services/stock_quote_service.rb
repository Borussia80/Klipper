require 'net/http'

class StockQuoteService
  BRAPI_URL = "https://brapi.dev/api/quote"
  CACHE_TTL = 15.minutes

  def self.fetch(tickers)
    new(tickers).fetch
  end

  def initialize(tickers)
    @tickers = Array(tickers).map(&:upcase).join(",")
  end

  def fetch
    cache_key = "quotes/#{@tickers}"
    Rails.cache.fetch(cache_key, expires_in: CACHE_TTL) do
      response = Net::HTTP.get(URI("#{BRAPI_URL}/#{@tickers}?fundamental=false"))
      data = JSON.parse(response)
      {
        quotes: parse_results(data),
        cached_at: Time.current.iso8601,
      }
    end
  end

  private

  def parse_results(data)
    (data["results"] || []).map do |r|
      {
        ticker:     r["symbol"],
        price:      r["regularMarketPrice"],
        change_pct: r["regularMarketChangePercent"],
        name:       r["longName"] || r["shortName"],
      }
    end
  end
end
