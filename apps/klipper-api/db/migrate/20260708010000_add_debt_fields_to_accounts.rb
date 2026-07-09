class AddDebtFieldsToAccounts < ActiveRecord::Migration[8.1]
  def change
    add_column :accounts, :saldo_fatura_atual, :decimal, precision: 15, scale: 2
    add_column :accounts, :pagamento_minimo,   :decimal, precision: 15, scale: 2
    add_column :accounts, :juros_rotativo_am,  :decimal, precision: 6,  scale: 3
    add_column :accounts, :juros_rotativo_aa,  :decimal, precision: 7,  scale: 3
    add_column :accounts, :iof_projetado,      :decimal, precision: 15, scale: 2
    add_column :accounts, :saldo_atualizado_em, :datetime
  end
end
