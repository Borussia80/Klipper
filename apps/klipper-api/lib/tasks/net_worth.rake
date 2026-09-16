# Correção pontual do FIN-002. Deliberadamente NÃO é uma migration: reescrever
# histórico financeiro é operação de dado, não de schema, e precisa ser disparada
# por quem está olhando o resultado. Rode com DRY_RUN=1 primeiro.
namespace :net_worth do
  desc "Recalcula investments_cost/net_worth dos snapshots gravados com venda somada (FIN-002). DRY_RUN=1 simula."
  task backfill: :environment do
    dry_run = ENV["DRY_RUN"].present?

    puts dry_run ? "== DRY RUN — nada será gravado ==" : "== Backfill de snapshots (FIN-002) =="

    NetWorthSnapshot.includes(:user).group_by(&:user).each do |user, snapshots|
      corrections = snapshots.filter_map do |snapshot|
        # O serviço original somava todas as operações existentes quando o job
        # rodou, sem recorte de data. Aqui o recorte é o fim do mês do snapshot,
        # via occurred_on: é a melhor reconstrução possível da população de
        # então, e evita puxar operação posterior para um mês anterior.
        cutoff = Date.new(snapshot.year, snapshot.month, -1)
        cost = user.investments
                   .where(occurred_on: ..cutoff)
                   .sum(Investment.signed_cost_sql)
                   .to_f.round(2)
        net = (snapshot.accounts_total.to_f + cost).round(2)

        next if cost == snapshot.investments_cost.to_f && net == snapshot.net_worth.to_f

        entry = {
          "year" => snapshot.year,
          "month" => snapshot.month,
          "investments_cost_before" => snapshot.investments_cost.to_f.to_s,
          "investments_cost_after" => cost.to_s,
          "net_worth_before" => snapshot.net_worth.to_f.to_s,
          "net_worth_after" => net.to_s
        }

        puts format("  user=%<user>d %<year>d-%<month>02d  custo %<before>s -> %<after>s  patrimônio %<nw_before>s -> %<nw_after>s",
          user: user.id, year: snapshot.year, month: snapshot.month,
          before: entry["investments_cost_before"], after: entry["investments_cost_after"],
          nw_before: entry["net_worth_before"], nw_after: entry["net_worth_after"])

        snapshot.update!(investments_cost: cost, net_worth: net) unless dry_run
        entry
      end

      next if corrections.empty? || dry_run

      AuditLog.create!(
        user: user,
        event_type: "BACKFILL_NET_WORTH",
        status: "success",
        record_count: corrections.size,
        metadata: { "corrections" => corrections }
      )
    end

    puts "== Fim =="
  end
end
