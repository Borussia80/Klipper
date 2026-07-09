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
    it { is_expected.to validate_inclusion_of(:natureza).in_array(Category::NATUREZAS) }
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

  describe "natureza scopes" do
    let(:user) { create(:user) }
    let!(:fixo)               { create(:category, :fixo, user: user) }
    let!(:cartao_parcelamento) { create(:category, :cartao_parcelamento, user: user) }
    let!(:variavel)           { create(:category, :variavel, user: user) }

    it "fixo scope returns only fixo categories" do
      expect(Category.fixo).to include(fixo)
      expect(Category.fixo).not_to include(cartao_parcelamento, variavel)
    end

    it "cartao_parcelamento scope returns only cartao_parcelamento categories" do
      expect(Category.cartao_parcelamento).to include(cartao_parcelamento)
      expect(Category.cartao_parcelamento).not_to include(fixo, variavel)
    end

    it "variavel scope returns only variavel categories" do
      expect(Category.variavel).to include(variavel)
      expect(Category.variavel).not_to include(fixo, cartao_parcelamento)
    end
  end

  describe "reimbursement link" do
    let(:user)  { create(:user) }
    let(:other_user) { create(:user) }
    let(:income) { create(:category, :income, user: user) }
    let(:expense) { create(:category, user: user) }

    it "accepts a valid expense→income link for the same user" do
      expense.reimbursed_by_category = income
      expect(expense).to be_valid
    end

    it "rejects a self-reference" do
      expense.reimbursed_by_category_id = expense.id
      expect(expense).not_to be_valid
      expect(expense.errors[:reimbursed_by_category_id]).to be_present
    end

    it "rejects the link when the owning category is not an expense" do
      income.reimbursed_by_category = create(:category, :income, user: user)
      expect(income).not_to be_valid
      expect(income.errors[:reimbursed_by_category_id]).to include("só pode ser definido em categorias de despesa")
    end

    it "rejects the link when the target is not an income category" do
      expense.reimbursed_by_category = create(:category, user: user)
      expect(expense).not_to be_valid
      expect(expense.errors[:reimbursed_by_category]).to include("deve ser uma categoria de receita")
    end

    it "rejects the link when the target belongs to another user" do
      expense.reimbursed_by_category = create(:category, :income, user: other_user)
      expect(expense).not_to be_valid
      expect(expense.errors[:reimbursed_by_category]).to include("deve pertencer ao mesmo usuário")
    end

    it "allows a nil link" do
      expense.reimbursed_by_category = nil
      expect(expense).to be_valid
    end

    it "nullifies the link when the reimbursed_by_category is destroyed" do
      linked_expense = create(:category, :with_reimbursement, user: user)
      income_target = linked_expense.reimbursed_by_category
      income_target.destroy!
      expect(linked_expense.reload.reimbursed_by_category_id).to be_nil
    end

    it "with_reimbursement_link scope returns only categories with a link set" do
      linked = create(:category, :with_reimbursement, user: user)
      unlinked = create(:category, user: user)
      expect(Category.with_reimbursement_link).to include(linked)
      expect(Category.with_reimbursement_link).not_to include(unlinked)
    end
  end
end
