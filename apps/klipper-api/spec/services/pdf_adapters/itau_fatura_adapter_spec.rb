require "rails_helper"
require "pdf/reader"

RSpec.describe PdfAdapters::ItauFaturaAdapter do
  FaturaFakeRun = Struct.new(:x, :y, :text)
  FaturaFakePage = Struct.new(:text, :runs)

  def fake_page(emission_line, rows)
    runs = rows.flat_map { |y, cells| cells.map { |x, text| FaturaFakeRun.new(x, y, text) } }
    FaturaFakePage.new(emission_line, runs)
  end

  def pages_for(path)
    PDF::Reader.new(path.to_s).pages
  end

  describe ".matches?" do
    it "reconhece marcadores de fatura Itaú" do
      expect(described_class.matches?("ResumodafaturaemR$ ...")).to eq(true)
      expect(described_class.matches?("Lanamentos:comprasesaques")).to eq(true)
    end

    it "não reconhece texto de extrato" do
      expect(described_class.matches?("agência:922conta:003163-8")).to eq(false)
    end
  end

  describe "#parse" do
    it "reconstrói colunas por posição, rastreia titular por coluna, infere ano e exclui não-lançamentos" do
      emission = "Emissão: 02/07/2026"
      rows = {
        100 => [ [ 10, "Lançamentos:comprasesaques" ], [ 400, "Lançamentos:comprasesaques" ] ],
        90  => [ [ 10, "TITULARUM(final1111)" ], [ 400, "01/02 MERCADOX 05/10 50,00" ] ],
        80  => [ [ 10, "05/12 LOJATESTE 20,00" ] ],
        70  => [ [ 10, "CATEGORIA .CIDADE" ] ],
        60  => [ [ 10, "Lançamentosnocartão(final1111) 20,00" ] ],
        50  => [ [ 400, "SEGUNDOTITULAR(final2222)" ] ],
        40  => [ [ 400, "10/06 LOJADOIS 15,50" ] ],
        30  => [ [ 10, "Lançamentosinternacionais" ] ],
        20  => [ [ 10, "13/06 FOREIGNMERCH 116,42" ] ],
        10  => [ [ 10, "CITY 100,00 USD 20,00" ] ],
        0   => [ [ 10, "Dólar de Conversão R$5,00" ] ],
        -10 => [ [ 10, "Lançamentos:produtoseservios" ] ],
        -20 => [ [ 10, "01/07 SERVICEX 30,00" ] ],
        -30 => [ [ 10, "Principal (R$ 25,00 ) + Juros (R$ 5,00 )" ] ],
        -40 => [ [ 10, "Lançamentosprodutoseservios 30,00" ] ],
        -50 => [ [ 10, "Compras parceladas - próximas faturas" ] ],
        -60 => [ [ 10, "01/08 FUTURECHARGE 99,00" ] ]
      }

      result = described_class.new([ fake_page(emission, rows) ]).parse
      descriptions = result.rows.map(&:description)

      expect(descriptions).to contain_exactly("MERCADOX", "LOJATESTE", "LOJADOIS", "FOREIGNMERCH", "SERVICEX")

      mercadox = result.rows.find { |r| r.description == "MERCADOX" }
      expect(mercadox.installment_number).to eq(5)
      expect(mercadox.installment_total).to eq(10)
      expect(mercadox.metadata[:cardholder]).to be_nil # ainda sem titular anunciado na coluna direita

      lojateste = result.rows.find { |r| r.description == "LOJATESTE" }
      expect(lojateste.occurred_on).to eq(Date.new(2025, 12, 5)) # mês > mês de emissão => ano anterior
      expect(lojateste.metadata[:cardholder]).to include("TITULARUM")

      lojadois = result.rows.find { |r| r.description == "LOJADOIS" }
      expect(lojadois.occurred_on).to eq(Date.new(2026, 6, 10))
      expect(lojadois.metadata[:cardholder]).to include("SEGUNDOTITULAR")

      foreign = result.rows.find { |r| r.description == "FOREIGNMERCH" }
      expect(foreign.metadata[:section]).to eq("internacional")
      expect(foreign.metadata[:original_currency]).to eq("USD")
      expect(foreign.amount).to eq(BigDecimal("-116.42")) # compra = débito, sinal invertido em relação ao valor impresso na fatura

      mercadox_row = result.rows.find { |r| r.description == "MERCADOX" }
      expect(mercadox_row.amount).to eq(BigDecimal("-50.00"))

      servicex = result.rows.find { |r| r.description == "SERVICEX" }
      expect(servicex.metadata[:principal]).to eq(BigDecimal("25.00"))
      expect(servicex.metadata[:juros]).to eq(BigDecimal("5.00"))
    end

    it "levanta ParseError quando a data de emissão não é encontrada" do
      page = fake_page("sem data de emissão aqui", { 10 => [ [ 10, "01/02 X 10,00" ] ] })
      expect { described_class.new([ page ]).parse }.to raise_error(PdfAdapters::ParseError, /emissão/)
    end

    it "levanta ParseError quando nenhum lançamento é reconhecido" do
      page = fake_page("Emissão: 02/07/2026", { 10 => [ [ 10, "texto qualquer" ] ] })
      expect { described_class.new([ page ]).parse }.to raise_error(PdfAdapters::ParseError, /Nenhum lançamento/)
    end

    it "extrai lançamentos reais da fatura Itaú (compras e saques, internacional, produtos e serviços)" do
      with_pdf_fixture("itau_fatura.pdf") do |path|
        result = described_class.new(pages_for(path)).parse

        amazon_rows = result.rows.select { |r| r.description == "AMAZONMKTPLC*BRINQ" }
        expect(amazon_rows.map { |r| [ r.installment_number, r.installment_total ] }).to contain_exactly([ 9, 10 ])

        current_charge = amazon_rows.first
        expect(current_charge.occurred_on).to eq(Date.new(2025, 10, 7)) # mês 10 > emissão (07) => ano anterior
        expect(current_charge.metadata[:cardholder]).to include("0460")

        anthropic = result.rows.find { |r| r.description.include?("ANTHROPIC") }
        expect(anthropic.metadata[:section]).to eq("internacional")
        expect(anthropic.amount).to eq(BigDecimal("-116.42")) # compra = débito, sinal invertido em relação ao valor impresso

        pix = result.rows.find { |r| r.description.include?("PIXOURTRIPVIAGEN") }
        expect(pix.metadata[:principal]).to eq(BigDecimal("140.03"))
        expect(pix.metadata[:juros]).to eq(BigDecimal("3.28"))
      end
    end
  end
end
