FactoryBot.define do
  factory :account do
    association :user
    name { Faker::Bank.name }
    institution { Faker::Bank.name }
    account_type { "checking" }
    balance { 0 }
    currency { "BRL" }
    active { true }

    trait :credit_card do
      account_type { "credit_card" }
    end

    # Dados reais da fatura Itaú Personnalité usada como fixture de regressão
    # (ver ROADMAP_KLIPPER_WEALTH_OS.md — Lacuna 5).
    trait :with_debt_data do
      credit_card
      saldo_fatura_atual { 9603.90 }
      pagamento_minimo   { 960.39 }
      juros_rotativo_am  { 12.92 }
      juros_rotativo_aa  { 435.0 }
      iof_projetado      { 60.12 }
    end

    trait :investment do
      account_type { "investment" }
    end

    trait :inactive do
      active { false }
    end
  end
end
