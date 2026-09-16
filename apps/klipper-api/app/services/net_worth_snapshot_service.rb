class NetWorthSnapshotService
  def self.call(user, at: Date.current)
    new(user, at: at).call
  end

  def initialize(user, at: Date.current)
    @user = user
    @at = at
  end

  def call
    accounts_total = @user.accounts.sum(:balance).to_f.round(2)
    investments_cost = @user.investments.sum(Investment.signed_cost_sql).to_f.round(2)

    @user.net_worth_snapshots.find_or_initialize_by(year: @at.year, month: @at.month).tap do |snapshot|
      snapshot.update!(
        accounts_total: accounts_total,
        investments_cost: investments_cost,
        net_worth: (accounts_total + investments_cost).round(2),
      )
    end
  end
end
