namespace :accounts do
  desc "Simula o impacto C-4 nos saldos, sem alterar dados (somente leitura)."
  task audit_opening_balances: :environment do
    puts "== DRY RUN C-4 — nenhuma alteração será gravada =="
    affected = 0
    Account.find_each do |account|
      entries = account.transactions.booked.kept.where("occurred_on < ?", account.opening_balance_on)
      next unless entries.exists?

      affected += 1
      delta = entries.sum(&:ledger_delta)
      all_movements = account.transactions.booked.kept.where("occurred_on <= ?", Date.current).sum(&:ledger_delta)
      legacy = account.opening_balance + all_movements
      puts format("account_id=%d currency=%s opening_on=%s entries=%d legacy=%.2f corrected=%.2f excluded_delta=%.2f",
        account.id, account.currency, account.opening_balance_on, entries.count, legacy, legacy - delta, delta)
    end
    puts "Contas verificadas: #{Account.count}; contas com histórico anterior à abertura: #{affected}"
  end
end
