FactoryBot.define do
  factory :net_worth_snapshot do
    association :user
    year  { Date.current.year }
    month { Date.current.month }
    accounts_total    { 1000.00 }
    investments_cost  { 500.00 }
    net_worth         { 1500.00 }
  end
end
