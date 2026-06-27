module Api
  module V1
    class ImportsController < BaseController
      before_action :authenticate_request!

      def create
        file = params[:file]
        return render json: { error: "Arquivo não enviado" }, status: :unprocessable_entity if file.blank?

        result = CsvImportService.new(
          @current_user,
          file,
          account_id: params[:account_id]
        ).call

        render json: { imported: result.imported, errors: result.errors }, status: :ok
      end
    end
  end
end
