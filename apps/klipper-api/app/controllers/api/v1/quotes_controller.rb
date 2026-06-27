module Api
  module V1
    class QuotesController < BaseController
      before_action :authenticate_request!

      def index
        tickers = params[:tickers]
        return render json: { error: "Parâmetro 'tickers' obrigatório" }, status: :unprocessable_entity if tickers.blank?

        result = StockQuoteService.fetch(tickers.split(","))
        render json: result
      rescue JSON::ParserError, SocketError, Net::OpenTimeout => e
        render json: { error: "Erro ao buscar cotações: #{e.message}" }, status: :service_unavailable
      end
    end
  end
end
