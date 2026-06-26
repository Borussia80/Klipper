FactoryBot.define do
  factory :investment do
    association :user
    name            { Faker::Company.name }
    ticker          { Faker::String.random(length: 5).upcase }
    investment_type { "stock" }
    quantity        { Faker::Number.decimal(l_digits: 2, r_digits: 4) }
    average_price   { Faker::Commerce.price(range: 5.0..200.0) }
    currency        { "BRL" }

    trait :fii do
      investment_type { "fii" }
    end

    trait :fixed_income do
      investment_type { "fixed_income" }
      ticker { nil }
    end
  end
end
