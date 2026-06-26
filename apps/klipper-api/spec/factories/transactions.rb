FactoryBot.define do
  factory :transaction do
    association :user
    association :account
    association :category
    description { Faker::Commerce.product_name }
    amount      { Faker::Commerce.price(range: 1.0..500.0) }
    transaction_type { "debit" }
    occurred_on { Faker::Date.backward(days: 30) }

    trait :credit do
      transaction_type { "credit" }
    end

    trait :transfer do
      transaction_type { "transfer" }
    end

    trait :with_installments do
      installment_total  { 12 }
      installment_number { 1 }
    end
  end
end
