FactoryBot.define do
  factory :member do
    association :user
    name { Faker::Name.name }
    relationship { "titular" }
    active { true }

    trait :dependente do
      relationship { "dependente" }
    end

    trait :inactive do
      active { false }
    end
  end
end
