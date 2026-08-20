require "rails_helper"

RSpec.describe AuditLog, type: :model do
  describe "associations" do
    it { is_expected.to belong_to(:user) }
  end

  describe "validations" do
    subject { build(:audit_log) }

    it { is_expected.to validate_presence_of(:event_type) }
    it { is_expected.to validate_presence_of(:user_id) }
    it { is_expected.to validate_presence_of(:record_count) }
    it { is_expected.to validate_presence_of(:status) }
    it { is_expected.to validate_numericality_of(:record_count).is_greater_than_or_equal_to(0) }

    it do
      is_expected.to validate_inclusion_of(:event_type)
        .in_array(%w[IMPORT_DATA EXPORT_DATA])
    end

    it do
      is_expected.to validate_inclusion_of(:status)
        .in_array(%w[success failure])
    end
  end

  describe "immutability" do
    it "is readonly after create" do
      audit_log = create(:audit_log)
      expect(audit_log).to be_readonly
    end

    it "prevents updates on persisted record" do
      audit_log = create(:audit_log)
      expect { audit_log.update!(record_count: 999) }.to raise_error(ActiveRecord::ReadOnlyRecord)
    end

    it "prevents destroy" do
      audit_log = create(:audit_log)
      expect { audit_log.destroy! }.to raise_error(ActiveRecord::ReadOnlyRecord)
    end
  end

  describe "enum-like query methods" do
    it "maps IMPORT_DATA event_type" do
      log = build(:audit_log, event_type: "IMPORT_DATA")
      expect(log.import_data?).to be true
      expect(log.export_data?).to be false
    end

    it "maps EXPORT_DATA event_type" do
      log = build(:audit_log, event_type: "EXPORT_DATA")
      expect(log.export_data?).to be true
      expect(log.import_data?).to be false
    end

    it "maps success status" do
      log = build(:audit_log, status: "success")
      expect(log.success?).to be true
      expect(log.failure?).to be false
    end

    it "maps failure status" do
      log = build(:audit_log, status: "failure")
      expect(log.failure?).to be true
      expect(log.success?).to be false
    end
  end

  describe "scopes and ordering" do
    it "orders by created_at descending by default" do
      user = create(:user)

      travel_to 1.day.ago do
        create(:audit_log, user: user, event_type: "IMPORT_DATA", status: "success", record_count: 5)
      end

      travel_to 1.hour.ago do
        create(:audit_log, user: user, event_type: "EXPORT_DATA", status: "success", record_count: 3)
      end

      result = AuditLog.recent_first
      expect(result.count).to eq(2)
      expect(result.first.event_type).to eq("EXPORT_DATA")
    end

    it "requires user_id to be present" do
      log = build(:audit_log, user: nil)
      expect(log).not_to be_valid
    end
  end
end
