module Api
  module V1
    class ImportsController < BaseController
      before_action :authenticate_request!

      def create
        file = params[:file]
        if file.blank?
          record_import_audit(status: "failure", record_count: 0)
          return render json: { error: "Arquivo não enviado" }, status: :unprocessable_entity
        end

        BankImport::FileGuard.ensure_valid!(file, expected: :csv)

        checksum = compute_checksum(file)

        result = CsvImportService.new(
          @current_user,
          file,
          account_id: params[:account_id]
        ).call

        total = result.imported + result.duplicates
        status = result.errors.empty? ? "success" : (total.positive? ? "success" : "failure")

        record_import_audit(status: status, record_count: total, checksum: checksum)

        render json: { imported: result.imported, duplicates: result.duplicates, errors: result.errors }, status: :ok
      rescue BankImport::FileGuard::InvalidFile => e
        record_import_audit(status: "failure", record_count: 0)
        render json: { error: e.message }, status: :unprocessable_entity
      end

      def preview
        file = params[:file]
        return render json: { error: "Arquivo não enviado" }, status: :unprocessable_entity if file.blank?

        BankImport::FileGuard.ensure_valid!(file, expected: :pdf)

        result = PdfImportService.new(@current_user, account_id: params[:account_id]).preview(file)

        if result.error?
          render json: { error: result.error }, status: :unprocessable_entity
        else
          render json: { adapter: result.adapter, rows: result.rows, warnings: result.warnings }, status: :ok
        end
      rescue BankImport::FileGuard::InvalidFile => e
        render json: { error: e.message }, status: :unprocessable_entity
      end

      def confirm
        result = PdfImportService.new(@current_user, account_id: params[:account_id]).confirm(confirm_rows)

        total = result.imported + result.duplicates
        status = result.errors.empty? ? "success" : (total.positive? ? "success" : "failure")

        record_import_audit(status: status, record_count: total)

        render json: { imported: result.imported, duplicates: result.duplicates, errors: result.errors }, status: :ok
      end

      private

      def confirm_rows
        permitted = params.permit(rows: [ :occurred_on, :description, :amount, :installment_number, :installment_total, :page, :member_id, :token ])[:rows] || []
        permitted.map(&:to_h)
      end

      def record_import_audit(status:, record_count:, checksum: nil)
        AuditLog.create!(
          user: @current_user,
          event_type: "IMPORT_DATA",
          status: status,
          record_count: record_count,
          checksum: checksum
        )
      end

      def compute_checksum(file)
        Digest::SHA256.hexdigest(file.read)
      ensure
        file.rewind rescue nil
      end
    end
  end
end
