module Api
  module V1
    class QuotesController < BaseController
      before_action :authenticate_request!

      def index
        tickers = params[:tickers]
        return render json: { error: "Parâmetro 'tickers' obrigatório" }, status: :unprocessable_entity if tickers.blank?

        result = StockQuoteService.fetch(tickers.split(","))
        render json: result
      rescue StockQuoteService::InvalidTicker => e
        # Entrada malformada é erro do chamador, não indisponibilidade do
        # brapi.dev: antes caía no 500 genérico (SEC-004).
        render json: { error: "Parâmetro 'tickers' inválido: #{e.message}" }, status: :unprocessable_entity
      rescue JSON::ParserError, SocketError, Net::OpenTimeout, Net::ReadTimeout => e
        render json: { error: "Erro ao buscar cotações: #{e.message}" }, status: :service_unavailable
      end
    end
  end
end
