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

  it "continua registrando os outros usuários quando um snapshot falha" do
    first = create(:user)
    failing = create(:user)
    last = create(:user)
    create(:account, user: first, balance: 100)
    create(:account, user: last, balance: 200)

    allow(NetWorthSnapshotService).to receive(:call).and_wrap_original do |original, user, **kwargs|
      raise ActiveRecord::RecordNotUnique if user == failing

      original.call(user, **kwargs)
    end
    allow(Rails.logger).to receive(:error)

    expect { described_class.perform_now }.not_to raise_error

    expect(first.net_worth_snapshots.find_by(year: Date.current.year, month: Date.current.month)).to be_present
    expect(last.net_worth_snapshots.find_by(year: Date.current.year, month: Date.current.month)).to be_present
    expect(Rails.logger).to have_received(:error).with(include("#{failing.id}"))
  end
end
