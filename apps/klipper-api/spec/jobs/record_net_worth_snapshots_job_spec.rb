require "rails_helper"

RSpec.describe RecordNetWorthSnapshotsJob, type: :job do
  it "records a snapshot for every user" do
    first = create(:user)
    second = create(:user)
    create(:account, user: first, balance: 100)
    create(:account, user: second, balance: 200)

    described_class.perform_now

    expect(first.net_worth_snapshots.find_by(year: Date.current.year, month: Date.current.month).net_worth.to_f).to eq(100.0)
    expect(second.net_worth_snapshots.find_by(year: Date.current.year, month: Date.current.month).net_worth.to_f).to eq(200.0)
  end
end
