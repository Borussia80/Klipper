# Agregação do relatório mensal, extraída de ReportsController#monthly.
# O controller já delegava reimbursement_coverage e debt_ranking a
# calculators e agregava monthly e natureza_split inline — dois padrões no
# mesmo arquivo, que é o ARCH-006.
#
# As três queries fixas (somas, contagens e categorias de uma vez) vieram
# inteiras do controller e são o conserto do N+1 que fazia o custo subir com o
# número de categorias do usuário. Extração não é oportunidade de reescrevê-las.
class MonthlySummaryCalculator
  def initialize(user, year:, month:, member_id: nil)
    @user = user
    @year = year
    @month = month
    @member_id = member_id
  end

  def call
    {
      total_debits: debits.to_f.round(2),
      total_credits: credits.to_f.round(2),
      net: (credits - debits).to_f.round(2),
      by_category: by_category
    }
  end

  # Fora do hash de `call` de propósito: o controller precisa deste número para
  # o log de auditoria de exportação, mas ele não faz parte do JSON da resposta.
  # Somá-lo ao retorno mudaria o contrato já consumido pelo front.
  def record_count
    transactions.count
  end

  private

  def transactions
    @transactions ||= begin
      txns = @user.transactions.in_month(@year, @month)
      @member_id ? txns.where(member_id: @member_id) : txns
    end
  end

  def debit_transactions
    @debit_transactions ||= transactions.where(transaction_type: "debit")
  end

  def debits
    @debits ||= debit_transactions.sum(:amount)
  end

  def credits
    @credits ||= transactions.where(transaction_type: "credit").sum(:amount)
  end

  def by_category
    totals = debit_transactions.group(:category_id).sum(:amount)
    counts = debit_transactions.group(:category_id).count
    categories = @user.categories.where(id: totals.keys.compact).index_by(&:id)

    totals.map do |cat_id, total|
      cat = categories[cat_id]
      {
        category_id: cat_id,
        category_name: cat&.name || "Sem categoria",
        category_icon: cat&.icon,
        total: total.to_f.round(2),
        count: counts[cat_id].to_i
      }
    end.sort_by { |r| -r[:total] }
  end
end
