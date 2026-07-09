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

        render json: { imported: result.imported, duplicates: result.duplicates, errors: result.errors }, status: :ok
      end

      def preview
        file = params[:file]
        return render json: { error: "Arquivo não enviado" }, status: :unprocessable_entity if file.blank?

        result = PdfImportService.new(@current_user, account_id: params[:account_id]).preview(file)

        if result.error?
          render json: { error: result.error }, status: :unprocessable_entity
        else
          render json: { adapter: result.adapter, rows: result.rows, warnings: result.warnings }, status: :ok
        end
      end

      def confirm
        result = PdfImportService.new(@current_user, account_id: params[:account_id]).confirm(confirm_rows)

        render json: { imported: result.imported, duplicates: result.duplicates, errors: result.errors }, status: :ok
      end

      private

      def confirm_rows
        permitted = params.permit(rows: [ :occurred_on, :description, :amount, :installment_number, :installment_total, :page, :member_id ])[:rows] || []
        permitted.map(&:to_h)
      end
    end
  end
end
