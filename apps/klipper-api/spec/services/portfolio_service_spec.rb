require "rails_helper"

RSpec.describe PortfolioService, type: :service do
  let(:user) { create(:user) }

  subject(:service) { described_class.new(user) }

  # Todas as linhas abaixo são operation_type: "buy" (default da factory), então a soma
  # sinalizada de total_cost coincide com a soma bruta antiga — este bloco caracteriza
  # o caso comum (só compras) e continua valendo com a mesma semântica de antes do fix.
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

  # total_cost passa a ser custo LÍQUIDO da posição (buy soma, sell subtrai), não mais a
  # soma bruta de todo lançamento histórico — este é o comportamento pós-fix do P0.1.
  context "with buy and sell operations on the same ticker" do
    before do
      create(:investment, user: user, ticker: "IVVB11",
        quantity: 10, average_price: 100)             # +1000
      create(:investment, :sell, user: user, ticker: "IVVB11",
        quantity: 4, average_price: 120)               # -480
    end

    describe "#totals" do
      it "nets the sell against the buy instead of summing both as cost" do
        result = service.totals
        expect(result[:total_positions]).to eq(2)
        expect(result[:total_cost]).to eq(520.0) # 1000 - 480, não 1480
      end
    end
  end

  # FIN-007: a porcentagem de alocação é uma fatia do custo líquido da carteira, e
  # o custo líquido pode chegar a zero ou negativo com posições reais no lugar —
  # basta vender o que se comprou, pelo preço de compra ou acima dele. Base zero
  # ou negativa não tem porcentagem, e o service devolvia 0,0% para todos os tipos,
  # que a tela desenhava como se fosse alocação medida.
  context "when the net cost of the portfolio is not positive" do
    describe "#allocation" do
      it "reports a nil percentage instead of 0.0 when the net cost is exactly zero" do
        create(:investment, user: user, ticker: "IVVB11", investment_type: "stock",
          quantity: 10, average_price: 100)                  # +1000
        create(:investment, :sell, user: user, ticker: "IVVB11", investment_type: "stock",
          quantity: 10, average_price: 100)                  # -1000

        row = service.allocation.find { |r| r[:investment_type] == "stock" }

        expect(row[:pct_of_portfolio]).to be_nil
        # O que existe continua sendo reportado: são as duas linhas e o custo
        # líquido delas. Só a razão é que não existe.
        expect(row[:count]).to eq(2)
        expect(row[:total_cost]).to eq(0.0)
      end

      it "reports a nil percentage when the position was sold above what it cost" do
        create(:investment, user: user, ticker: "IVVB11", investment_type: "stock",
          quantity: 10, average_price: 100)                  # +1000
        create(:investment, :sell, user: user, ticker: "IVVB11", investment_type: "stock",
          quantity: 10, average_price: 150)                  # -1500

        row = service.allocation.find { |r| r[:investment_type] == "stock" }

        expect(row[:pct_of_portfolio]).to be_nil
        expect(row[:total_cost]).to eq(-500.0)
      end

      # O nil vem da base, que é única para a carteira toda, então ele não é
      # privilégio do tipo que ficou negativo: um tipo com custo líquido positivo
      # na mesma carteira também perde a porcentagem, porque não há denominador.
      it "nils the percentage of every type, not only the one that went negative" do
        create(:investment, user: user, ticker: "IVVB11", investment_type: "stock",
          quantity: 10, average_price: 100)                  # +1000
        create(:investment, :sell, user: user, ticker: "IVVB11", investment_type: "stock",
          quantity: 10, average_price: 300)                  # -3000
        create(:investment, :fii, user: user, ticker: "HGLG11",
          quantity: 20, average_price: 50)                   # +1000, e segue positivo

        rows = service.allocation
        expect(rows.map { |r| r[:investment_type] }).to contain_exactly("stock", "fii")
        expect(rows.map { |r| r[:pct_of_portfolio] }).to all(be_nil)
        # Custo líquido da carteira: 1000 - 3000 + 1000 = -1000.
        expect(rows.find { |r| r[:investment_type] == "fii" }[:total_cost]).to eq(1000.0)
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
