# D1 (docs/domain-research/03-specs/03-lancamentos.md, L-1 e L-2): kind diz o que
# o lançamento é; status, se já aconteceu. Aditiva: todo lançamento existente
# nasce regular e efetivado, exceto os gravados com transaction_type "transfer",
# que passam a kind "transfer". Reclassificar pagamentos de fatura e estornos já
# gravados é operação de dado, com DRY_RUN: rake transactions:reclassify_kinds.
class AddKindAndStatusToTransactions < ActiveRecord::Migration[8.1]
  def up
    add_column :transactions, :kind, :string, null: false, default: "regular"
    add_column :transactions, :status, :string, null: false, default: "efetivado"
    add_index :transactions, [ :user_id, :kind, :occurred_on ]
    execute "UPDATE transactions SET kind = 'transfer' WHERE transaction_type = 'transfer'"
  end

  def down
    remove_index :transactions, [ :user_id, :kind, :occurred_on ]
    remove_column :transactions, :status
    remove_column :transactions, :kind
  end
end
