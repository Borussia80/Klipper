FactoryBot.define do
  factory :audit_log do
    association :user
    event_type   { "IMPORT_DATA" }
    status       { "success" }
    record_count { 10 }
    checksum     { nil }
    metadata     { {} }
  end
end
