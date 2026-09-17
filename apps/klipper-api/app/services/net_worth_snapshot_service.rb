class NetWorthSnapshotService
  # Soma sem persistir, para quem só quer o número. ReportsController#net_worth
  # tinha a mesma fórmula reimplementada, e divergência entre as duas já causou
  # bug real: no FIN-002 a venda entrava somando de um lado e subtraindo do
  # outro, então o snapshot persistido e a tela de relatório mostravam
  # patrimônios diferentes para o mesmo usuário (ARCH-003).
  #
  # Sem parâmetro `at:`, apesar de o ADR-2026-09-17-004 prevê-lo: nenhuma das
  # duas implementações filtrava por data. O `at` do #call escolhe só o mês da
  # chave do snapshot, não a data dos saldos. Aceitar um `at:` aqui e ignorá-lo
  # faria a assinatura prometer "patrimônio em X" que o método não entrega — a
  # mesma classe de divergência silenciosa que a extração existe para eliminar.
  def self.compute(user)
    accounts_total = user.accounts.sum(:balance).to_f.round(2)
    investments_cost = user.investments.sum(Investment.signed_cost_sql).to_f.round(2)

    {
      accounts_total: accounts_total,
      investments_cost: investments_cost,
      net_worth: (accounts_total + investments_cost).round(2)
    }
  end

  def self.call(user, at: Date.current)
    new(user, at: at).call
  end

  def initialize(user, at: Date.current)
    @user = user
    @at = at
  end

  def call
    @user.net_worth_snapshots.find_or_initialize_by(year: @at.year, month: @at.month).tap do |snapshot|
      snapshot.update!(**self.class.compute(@user))
    end
  end
end
