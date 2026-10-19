require "rails_helper"

RSpec.describe User, type: :model do
  describe "validations" do
    subject { build(:user) }

    it { is_expected.to have_secure_password }
    it { is_expected.to validate_presence_of(:email) }
    it { is_expected.to validate_uniqueness_of(:email).case_insensitive }
    it { is_expected.to validate_length_of(:password).is_at_least(8) }
  end

  describe "email normalization" do
    it "downcases email before save" do
      user = create(:user, email: "TEST@EXAMPLE.COM")
      expect(user.reload.email).to eq("test@example.com")
    end
  end

  describe "own identity" do
    it "returns an identity for registered names and CPF mask" do
      user = build(:user, own_names: [ "Jose Teste Da Silva" ], own_cpf_mask: "123.456")

      expect(user.own_identity).to have_attributes(names: [ "Jose Teste Da Silva" ], cpf_mask: "123.456")
    end

    it "returns nil when no own name is registered" do
      expect(build(:user, own_names: []).own_identity).to be_nil
    end
  end

  describe "own identity validations" do
    it "accepts at most five names with up to 80 characters and a valid CPF mask" do
      user = build(:user, own_names: Array.new(5) { "Jose Teste Da Silva" }, own_cpf_mask: "123.456-78")

      expect(user).to be_valid
    end

    it "rejects invalid own identity values" do
      user = build(:user, own_names: Array.new(6, "Jose Teste Da Silva"), own_cpf_mask: "123/456")

      expect(user).to be_invalid
      expect(user.errors[:own_names]).to be_present
      expect(user.errors[:own_cpf_mask]).to be_present
    end
  end
end
