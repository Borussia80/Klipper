require "rails_helper"

RSpec.describe "Audit Logs API", type: :request do
  let(:user)    { create(:user) }
  let(:headers) { auth_headers_for(user) }

  describe "GET /api/v1/audit_logs" do
    it "returns 401 without token" do
      get "/api/v1/audit_logs"
      expect(response).to have_http_status(:unauthorized)
    end

    it "returns empty list when no logs exist" do
      get "/api/v1/audit_logs", headers: headers

      expect(response).to have_http_status(:ok)
      expect(json_response).to eq([])
    end

    it "returns only current user's audit logs" do
      my_log = create(:audit_log, user: user, event_type: "IMPORT_DATA",
                                  status: "success", record_count: 10)
      other_log = create(:audit_log, user: create(:user), event_type: "EXPORT_DATA",
                                     status: "success", record_count: 5)

      get "/api/v1/audit_logs", headers: headers

      expect(response).to have_http_status(:ok)
      ids = json_response.map { |l| l[:id] }
      expect(ids).to include(my_log.id)
      expect(ids).not_to include(other_log.id)
    end

    it "returns logs ordered by most recent first" do
      freeze_time

      travel_to 3.days.ago do
        create(:audit_log, user: user, event_type: "IMPORT_DATA", status: "success", record_count: 3)
      end

      travel_to 1.hour.ago do
        create(:audit_log, user: user, event_type: "EXPORT_DATA", status: "success", record_count: 7)
      end

      get "/api/v1/audit_logs", headers: headers

      expect(response).to have_http_status(:ok)
      expect(json_response.length).to eq(2)
      expect(json_response.first[:event_type]).to eq("EXPORT_DATA")
      expect(json_response.first[:record_count]).to eq(7)
      expect(json_response.last[:event_type]).to eq("IMPORT_DATA")
      expect(json_response.last[:record_count]).to eq(3)
    end

    it "includes all expected fields in response" do
      create(:audit_log, user: user, event_type: "IMPORT_DATA", status: "success",
                         record_count: 42, checksum: "abc123", metadata: { format: "csv" })

      get "/api/v1/audit_logs", headers: headers

      log = json_response.first
      expect(log.keys).to match_array(%i[id event_type status record_count checksum metadata created_at])
      expect(log[:event_type]).to eq("IMPORT_DATA")
      expect(log[:status]).to eq("success")
      expect(log[:record_count]).to eq(42)
      expect(log[:checksum]).to eq("abc123")
      expect(log[:metadata]).to eq({ format: "csv" })
    end

    it "does not expose update/destroy endpoints" do
      log = create(:audit_log, user: user, event_type: "IMPORT_DATA", status: "success", record_count: 5)

      patch "/api/v1/audit_logs/#{log.id}", params: { record_count: 99 }.to_json, headers: headers
      expect(response).to have_http_status(:not_found)

      delete "/api/v1/audit_logs/#{log.id}", headers: headers
      expect(response).to have_http_status(:not_found)
    end
  end
end
