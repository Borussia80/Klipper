require "rails_helper"
require "pdf/reader"

RSpec.describe PdfAdapters::NubankFaturaAdapter do
  NubankFakePage = Struct.new(:text)

  def fake_page(text)
    NubankFakePage.new(text)
  end

  def pages_for(path)
    PDF::Reader.new(path.to_s).pages
  end

  describe ".matches?" do
    it "reconhece marcadores de fatura Nubank" do
      expect(described_class.matches?("... sua conta Nubank ... RESUMO DA FATURA ATUAL ...")).to eq(true)
    end

    it "não reconhece texto de outro layout" do
      expect(described_class.matches?("agência:922conta:003163-8")).to eq(false)
      expect(described_class.matches?("ResumodafaturaemR$ ...")).to eq(false)
    end
  end

  describe "#parse" do
    it "extrai lançamentos, rastreia titular, trata seção Pagamentos sem titular e infere ano" do
      text = <<~TEXT
        EMISSÃO E ENVIO 03 JUL 2026
        TRANSAÇÕES            DE 03 JUN A 03 JUL
        Roberto W C Milet                                    R$ 159,73
        19 JUN        •••• 5680  Conta Vivo                  R$ 159,73
        Pagamentos                                            -R$ 160,00
        10 JUN           Pagamento em 10 JUN                 -R$ 160,00
        01 AGO        •••• 5680  Compra Futura                R$ 40,00
      TEXT

      result = described_class.new([ fake_page(text) ]).parse
      descriptions = result.rows.map(&:description)

      expect(descriptions).to contain_exactly("Conta Vivo", "Pagamento em 10 JUN", "Compra Futura")

      compra = result.rows.find { |r| r.description == "Conta Vivo" }
      expect(compra.occurred_on).to eq(Date.new(2026, 6, 19))
      expect(compra.metadata[:cardholder]).to eq("Roberto W C Milet")
      expect(compra.metadata[:card_last4]).to eq("5680")
      expect(compra.amount).to eq(BigDecimal("-159.73")) # compra = débito, sinal invertido em relação ao valor impresso

      pagamento = result.rows.find { |r| r.description == "Pagamento em 10 JUN" }
      expect(pagamento.metadata[:cardholder]).to be_nil # seção "Pagamentos" não tem titular
      expect(pagamento.amount).to eq(BigDecimal("160.00")) # pagamento = crédito, sinal invertido em relação ao valor impresso

      futura = result.rows.find { |r| r.description == "Compra Futura" }
      expect(futura.occurred_on).to eq(Date.new(2025, 8, 1)) # mês (08) > mês de emissão (07) => ano anterior
    end

    it "ignora linhas com formato de cabeçalho/subtotal fora da seção TRANSAÇÕES" do
      text = <<~TEXT
        EMISSÃO E ENVIO 03 JUL 2026
        Pagamento mínimo para não ficar em atraso R$ 23,95
        TRANSAÇÕES            DE 03 JUN A 03 JUL
        19 JUN        •••• 5680  Conta Vivo                  R$ 159,73
      TEXT

      result = described_class.new([ fake_page(text) ]).parse

      expect(result.rows.length).to eq(1)
      expect(result.rows.first.metadata[:cardholder]).to be_nil # nenhum cabeçalho de titular apareceu dentro da seção
    end

    it "levanta ParseError quando a data de emissão não é encontrada" do
      text = <<~TEXT
        TRANSAÇÕES            DE 03 JUN A 03 JUL
        19 JUN        •••• 5680  Conta Vivo                  R$ 159,73
      TEXT

      expect { described_class.new([ fake_page(text) ]).parse }.to raise_error(PdfAdapters::ParseError, /emissão/)
    end

    it "levanta ParseError quando nenhum lançamento é reconhecido" do
      text = <<~TEXT
        EMISSÃO E ENVIO 03 JUL 2026
        TRANSAÇÕES            DE 03 JUN A 03 JUL
        texto qualquer sem lançamento
      TEXT

      expect { described_class.new([ fake_page(text) ]).parse }.to raise_error(PdfAdapters::ParseError, /Nenhum lançamento/)
    end

    it "SEC-21: rejeita rapidamente linha >500 chars sem backtracking catastrófico no TRANSACTION_ROW" do
      long_desc = "SUPERLOJA" * 250
      text = <<~TEXT
        EMISSÃO E ENVIO 03 JUL 2026
        TRANSAÇÕES            DE 03 JUN A 03 JUL
        19 JUN        •••• 5680  #{long_desc}                  R$ 159,73
        10 JUN           Pagamento em 10 JUN                 -R$ 160,00
      TEXT

      adapter = described_class.new([ fake_page(text) ])

      start = Process.clock_gettime(Process::CLOCK_MONOTONIC)
      result = adapter.parse
      elapsed = Process.clock_gettime(Process::CLOCK_MONOTONIC) - start

      expect(elapsed).to be < 1.0, "linha longa travou o regex por #{elapsed.round(2)}s"
      expect(result.rows.size).to eq(1)
      expect(result.rows.first.description).to eq("Pagamento em 10 JUN")
    end

    it "extrai lançamentos reais da fatura Nubank" do
      with_pdf_fixture("nubank_fatura.pdf") do |path|
        result = described_class.new(pages_for(path)).parse

        compra = result.rows.find { |r| r.description == "Conta Vivo" }
        expect(compra.occurred_on).to eq(Date.new(2026, 6, 19))
        expect(compra.metadata[:cardholder]).to eq("Roberto W C Milet")
        expect(compra.amount).to eq(BigDecimal("-159.73"))

        pagamento = result.rows.find { |r| r.description == "Pagamento em 10 JUN" }
        expect(pagamento.metadata[:cardholder]).to be_nil
        expect(pagamento.amount).to eq(BigDecimal("160.00"))
      end
    end
  end
end
