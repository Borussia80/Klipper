# Categorias em dois níveis (Fatia 1 de UX). Só acrescenta colunas que aceitam
# nulo: toda categoria existente continua raiz, sem posição e sem mesclagem.
#
# As FKs anulam em vez de restringir no banco porque a exclusão do usuário
# destrói as categorias em ordem de id, e um pai costuma vir antes das filhas.
# A proibição de excluir um pai com filhas fica no model, onde a cascata do
# usuário pode ser distinguida de uma exclusão direta.
class AddHierarchyToCategories < ActiveRecord::Migration[8.1]
  def change
    add_reference :categories, :parent, foreign_key: { to_table: :categories, on_delete: :nullify }
    add_reference :categories, :merged_into, foreign_key: { to_table: :categories, on_delete: :nullify }
    add_column :categories, :position, :integer
  end
end
