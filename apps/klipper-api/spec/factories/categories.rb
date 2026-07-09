FactoryBot.define do
  factory :category do
    association :user
    name  { Faker::Commerce.department(max: 1) }
    icon  { "shopping" }
    category_type { "expense" }
    natureza { "variavel" }
    color { "#6B93AE" }
    active { true }

    trait :income do
      category_type { "income" }
      icon { "income" }
    end

    trait :transfer do
      category_type { "transfer" }
      icon { "transfer" }
    end

    trait :inactive do
      active { false }
    end

    trait :fixo do
      natureza { "fixo" }
    end

    trait :cartao_parcelamento do
      natureza { "cartao_parcelamento" }
    end

    trait :variavel do
      natureza { "variavel" }
    end

    trait :with_reimbursement do
      reimbursed_by_category { association :category, :income, user: user }
    end
  end
end
