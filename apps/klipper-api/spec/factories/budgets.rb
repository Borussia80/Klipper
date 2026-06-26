FactoryBot.define do
  factory :budget do
    association :user
    association :category
    amount_limit  { Faker::Commerce.price(range: 100.0..2000.0) }
    period_month  { Date.today.month }
    period_year   { Date.today.year }
  end
end
