require "net/http"

class StockQuoteService
  BRAPI_URL = "https://brapi.dev/api/quote"
  CACHE_TTL = 15.minutes

  # O ticker vem do usuário e é interpolado no path da URL de saída e na chave
  # de cache. Sem um charset restrito, "PETR4/../../outra-rota" ou "X?foo=bar"
  # viram segmentos extras de path/query na requisição ao brapi.dev, e entrada
  # malformada derruba a ação com 500 (SEC-004). Ponto e letra/dígito cobrem
  # todos os formatos reais da B3 e de ADRs — PETR4, BOVA11, AAPL, BRK.B.
  TICKER_FORMAT = /\A[A-Z0-9.]{1,10}\z/

  InvalidTicker = Class.new(ArgumentError)

  def self.fetch(tickers)
    new(tickers).fetch
  end

  def initialize(tickers)
    list = Array(tickers).map { |t| t.to_s.strip.upcase }
    raise InvalidTicker, "nenhum ticker informado" if list.empty?

    invalid = list.reject { |t| t.match?(TICKER_FORMAT) }
    raise InvalidTicker, "ticker inválido: #{invalid.join(', ')}" if invalid.any?

    @tickers = list.join(",")
  end

  def fetch
    cache_key = "quotes/#{@tickers}"
    Rails.cache.fetch(cache_key, expires_in: CACHE_TTL) do
      response = Net::HTTP.get(URI("#{BRAPI_URL}/#{@tickers}?fundamental=false"))
      data = JSON.parse(response)
      {
        quotes: parse_results(data),
        cached_at: Time.current.iso8601
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
        name:       r["longName"] || r["shortName"]
      }
    end
  end
end
