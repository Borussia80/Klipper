FactoryBot.define do
  factory :category do
    association :user
    name  { Faker::Commerce.department(max: 1) }
    icon  { "shopping" }
    category_type { "expense" }
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
  end
end
