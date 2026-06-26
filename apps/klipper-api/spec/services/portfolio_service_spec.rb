require "rails_helper"

RSpec.describe PortfolioService, type: :service do
  let(:user) { create(:user) }

  subject(:service) { described_class.new(user) }

  context "with investments" do
    before do
      create(:investment, user: user, investment_type: "stock",
        quantity: 10, average_price: 100)    # cost: 1000
      create(:investment, user: user, investment_type: "stock",
        quantity: 5, average_price: 200)     # cost: 1000
      create(:investment, :fii, user: user,
        quantity: 20, average_price: 50)     # cost: 1000
    end

    describe "#totals" do
      it "returns correct total cost and count" do
        result = service.totals
        expect(result[:total_positions]).to eq(3)
        expect(result[:total_cost]).to eq(3000.0)
      end

      it "includes by_type breakdown" do
        result = service.totals
        expect(result[:by_type]).to be_an(Array)
        expect(result[:by_type].length).to eq(2)
      end
    end

    describe "#allocation" do
      it "calculates percentage per type" do
        result = service.allocation
        stock = result.find { |r| r[:investment_type] == "stock" }
        fii   = result.find { |r| r[:investment_type] == "fii" }

        expect(stock[:pct_of_portfolio]).to eq(66.7)
        expect(fii[:pct_of_portfolio]).to eq(33.3)
      end

      it "sorts by total_cost descending" do
        result = service.allocation
        costs = result.map { |r| r[:total_cost] }
        expect(costs).to eq(costs.sort.reverse)
      end
    end
  end

  context "with no investments" do
    describe "#totals" do
      it "returns zeros" do
        result = service.totals
        expect(result[:total_positions]).to eq(0)
        expect(result[:total_cost]).to eq(0)
        expect(result[:by_type]).to be_empty
      end
    end
  end
end
