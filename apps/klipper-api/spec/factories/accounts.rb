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

    trait :investment do
      account_type { "investment" }
    end

    trait :inactive do
      active { false }
    end
  end
end
