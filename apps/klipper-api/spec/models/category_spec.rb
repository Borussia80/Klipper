require "rails_helper"

RSpec.describe Category, type: :model do
  describe "associations" do
    it { is_expected.to belong_to(:user) }
  end

  describe "validations" do
    subject { build(:category) }

    it { is_expected.to validate_presence_of(:name) }
    it { is_expected.to validate_length_of(:name).is_at_most(80) }
    it { is_expected.to validate_inclusion_of(:category_type).in_array(Category::CATEGORY_TYPES) }
    it { is_expected.to validate_presence_of(:icon) }
  end

  describe "color validation" do
    it "accepts valid hex colors" do
      expect(build(:category, color: "#FF5733")).to be_valid
      expect(build(:category, color: "#abc123")).to be_valid
    end

    it "rejects invalid hex colors" do
      expect(build(:category, color: "red")).not_to be_valid
      expect(build(:category, color: "#GGG")).not_to be_valid
    end

    it "allows blank color" do
      expect(build(:category, color: "")).to be_valid
    end
  end

  describe "scopes" do
    let(:user) { create(:user) }
    let!(:expense)  { create(:category, user: user, category_type: "expense") }
    let!(:income)   { create(:category, :income, user: user) }
    let!(:inactive) { create(:category, :inactive, user: user) }

    it "active scope excludes inactive" do
      expect(Category.active).to include(expense, income)
      expect(Category.active).not_to include(inactive)
    end

    it "expenses scope returns only expense categories" do
      expect(Category.expenses).to include(expense)
      expect(Category.expenses).not_to include(income)
    end

    it "incomes scope returns only income categories" do
      expect(Category.incomes).to include(income)
      expect(Category.incomes).not_to include(expense)
    end
  end
end
