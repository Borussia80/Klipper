class DebtRankingCalculator
  def initialize(user)
    @user = user
  end

  def ranking
    cards.map { |account| build_row(account) }
         .sort_by { |row| [ -row[:encargos], -row[:saldo_fatura_atual], row[:account_id] ] }
  end

  private

  def cards
    @user.accounts.active.by_type("credit_card").with_debt_data
  end

  def build_row(account)
    financiado = [ account.saldo_fatura_atual - (account.pagamento_minimo || 0), 0 ].max
    encargos = financiado * (account.juros_rotativo_am / 100)
    iof = account.iof_projetado || 0

    {
      account_id: account.id,
      name: account.name,
      institution: account.institution,
      saldo_fatura_atual: account.saldo_fatura_atual.to_f.round(2),
      pagamento_minimo: account.pagamento_minimo&.to_f&.round(2),
      juros_rotativo_am: account.juros_rotativo_am.to_f.round(3),
      juros_rotativo_aa: account.juros_rotativo_aa&.to_f&.round(3),
      iof_projetado: account.iof_projetado&.to_f&.round(2),
      encargos: encargos.to_f.round(2),
      saldo_projetado_proximo_mes: (account.saldo_fatura_atual + encargos + iof).to_f.round(2),
      saldo_atualizado_em: account.saldo_atualizado_em,
    }
  end
end
