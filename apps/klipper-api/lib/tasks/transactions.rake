# M2 do plano (D1, decisão Q6): reclassifica lançamentos já gravados com a mesma
# detecção da importação (BankImport::KindDetector). Deliberadamente NÃO é uma
# migration: muda receita e despesa de meses fechados, e precisa ser disparada
# por quem aprovou o relatório. Rode com DRY_RUN=1 primeiro; VERBOSE=1 lista as
# linhas.
namespace :transactions do
  desc "Marca pagamentos de fatura e estornos já gravados (D1). DRY_RUN=1 simula; VERBOSE=1 lista as linhas."
  task reclassify_kinds: :environment do
    dry_run = ENV["DRY_RUN"].present?
    verbose = ENV["VERBOSE"].present?

    puts dry_run ? "== DRY RUN — nada será gravado ==" : "== Reclassificação de kind (D1) =="

    changes = Transaction.where(kind: "regular").find_each.filter_map do |t|
      signed = t.transaction_type == "debit" ? -t.amount : t.amount
      kind = BankImport::KindDetector.call(description: t.description, amount: signed)
      [ t, kind ] unless kind == "regular"
    end

    changes.group_by { |(t, _)| [ t.user_id, t.occurred_on.strftime("%Y-%m") ] }.sort.each do |(user_id, month), rows|
      by_kind = rows.group_by(&:last)
      income_drop  = rows.sum { |(t, k)| k == "card_payment" && t.transaction_type == "credit" ? t.amount : 0 }
      expense_drop = rows.sum { |(t, k)| k == "card_payment" && t.transaction_type == "debit" ? t.amount : 0 }
      refunds      = by_kind.fetch("refund", []).sum { |(t, _)| t.amount }
      puts format("usuário %d · %s · card_payment %d · refund %d · renda −%.2f · despesa −%.2f (pagamentos) −%.2f (estornos)",
        user_id, month, by_kind.fetch("card_payment", []).size, by_kind.fetch("refund", []).size,
        income_drop, expense_drop, refunds)
      next unless verbose

      rows.each { |(t, k)| puts "  ##{t.id} #{t.occurred_on} #{t.transaction_type} #{t.amount.to_s('F')} → #{k}" }
    end

    puts "Total: #{changes.size} lançamento(s)"
    next if dry_run

    Transaction.transaction do
      changes.each do |(t, kind)|
        attrs = { kind: kind }
        attrs[:category_id] = nil if kind == "card_payment"
        t.update!(attrs)
      end
    end
    puts "Gravado."
  end

  # D5 (spec 06, I-1 a I-3a): preenche external_id dos lançamentos legados
  # somente depois de revisão. Deliberadamente NÃO é uma migration: a regra usa
  # a normalização atual e precisa poder ser simulada com DRY_RUN=1; VERBOSE=1
  # lista as linhas que receberiam o identificador.
  desc "Preenche external_id dos lançamentos com conta. DRY_RUN=1 simula; VERBOSE=1 lista as linhas."
  task backfill_external_ids: :environment do
    dry_run = ENV["DRY_RUN"].present?
    verbose = ENV["VERBOSE"].present?

    puts dry_run ? "== DRY RUN — nada será gravado ==" : "== Backfill de external_id (D5) =="

    changes = Transaction.where.not(account_id: nil).distinct.order(:account_id).pluck(:account_id).flat_map do |account_id|
      account = Account.find(account_id)
      BankImport::ExternalIdBackfill.new(account).call(dry_run: true)
    end

    changes.group_by { |(transaction, _)| [ transaction.user_id, transaction.account_id ] }.sort.each do |(user_id, account_id), rows|
      puts format("usuário %d · conta %d · external_id %d", user_id, account_id, rows.size)
      next unless verbose

      rows.each { |(transaction, external_id)| puts "  ##{transaction.id} → #{external_id}" }
    end

    puts "Total: #{changes.size} lançamento(s)"
    next if dry_run

    changes.group_by { |(transaction, _)| transaction.account_id }.each_value do |account_changes|
      BankImport::ExternalIdBackfill.new(account_changes.first.first.account).call
    end
    puts "Gravado."
  end
end
