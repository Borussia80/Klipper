require "rails_helper"

RSpec.describe Member, type: :model do
  describe "associations" do
    it { is_expected.to belong_to(:user) }
  end

  describe "validations" do
    subject { build(:member) }

    it { is_expected.to validate_presence_of(:name) }
    it { is_expected.to validate_length_of(:name).is_at_most(100) }
    it { is_expected.to validate_inclusion_of(:relationship).in_array(Member::RELATIONSHIPS) }
  end

  describe "scopes" do
    let(:user) { create(:user) }
    let!(:active_member)   { create(:member, user: user, active: true) }
    let!(:inactive_member) { create(:member, :inactive, user: user) }

    it "active scope returns only active members" do
      expect(Member.active).to include(active_member)
      expect(Member.active).not_to include(inactive_member)
    end
  end
end
