# Mescla a categoria de origem na de destino (Fatia 1 de UX,
# docs/ux-research/05-specs/07-categorias.md). Tudo numa transação: ou a
# origem sai inteira para o destino, ou nada muda.
#
# A origem não é apagada: fica inativa com merged_into_id, para que o histórico
# e as regras que a procuram pelo nome continuem chegando ao destino.
class CategoryMergeService
  InvalidMerge = Class.new(StandardError)

  def self.call(source:, into:)
    new(source, into).call
  end

  def initialize(source, into)
    @source = source
    @into = into
  end

  def call
    validate!

    ActiveRecord::Base.transaction do
      move_transactions
      move_budgets
      move_reimbursement_links
      move_children
      @source.update!(active: false, merged_into_id: @into.id)
    end

    @into
  end

  private

  def validate!
    raise InvalidMerge, "não é possível mesclar uma categoria nela mesma" if @source.id == @into.id
    raise InvalidMerge, "as categorias são de usuários diferentes" unless @source.user_id == @into.user_id
    raise InvalidMerge, "as categorias são de tipos diferentes" unless @source.category_type == @into.category_type
    raise InvalidMerge, "a categoria de destino está inativa" unless @into.active

    if @into.parent_id.present? && @source.children.exists?
      raise InvalidMerge, "categoria com subcategorias só pode ser mesclada em uma categoria principal"
    end
  end

  def move_transactions
    Transaction.where(category_id: @source.id).update_all(category_id: @into.id, updated_at: Time.current)
  end

  # O índice único (usuário, categoria, ano, mês) impede dois orçamentos do
  # destino no mesmo mês; na colisão, os limites se somam.
  def move_budgets
    Budget.where(category_id: @source.id).find_each do |budget|
      existing = Budget.find_by(user_id: budget.user_id, category_id: @into.id,
        period_year: budget.period_year, period_month: budget.period_month)

      if existing
        existing.update!(amount_limit: existing.amount_limit + budget.amount_limit)
        budget.destroy!
      else
        budget.update!(category_id: @into.id)
      end
    end
  end

  def move_reimbursement_links
    Category.where(reimbursed_by_category_id: @source.id)
      .update_all(reimbursed_by_category_id: @into.id, updated_at: Time.current)
  end

  def move_children
    Category.where(parent_id: @source.id).update_all(parent_id: @into.id, updated_at: Time.current)
  end
end
