require "rails_helper"
require "pdf/reader"

RSpec.describe PdfAdapters::ItauExtratoAdapter do
  ExtratoFakePage = Struct.new(:text)

  def pages_for(path)
    PDF::Reader.new(path.to_s).pages
  end

  def fake_pages(*texts)
    texts.map { |t| ExtratoFakePage.new(t) }
  end

  describe ".matches?" do
    it "reconhece o cabeçalho de agência/conta do extrato Itaú" do
      text = "ROBERTO WAGNER 002.633.105-5agência:922conta:003163-8"
      expect(described_class.matches?(text)).to eq(true)
    end

    it "não reconhece texto sem o padrão agência/conta" do
      expect(described_class.matches?("fatura cartão de crédito")).to eq(false)
    end
  end

  describe "#parse" do
    it "extrai lançamentos reais e exclui linhas de SALDO DO DIA" do
      with_pdf_fixture("itau_extrato.pdf") do |path|
        result = described_class.new(pages_for(path)).parse

        expect(result.rows).not_to be_empty
        expect(result.rows).to all(be_a(PdfAdapters::Row))

        descriptions = result.rows.map(&:description)
        expect(descriptions.none? { |d| d.gsub(/\s+/, "").downcase == "saldododia" }).to eq(true)

        pix_row = result.rows.find { |r| r.raw_line.include?("PIXTRANSFJOAOPA31/12") }
        expect(pix_row).not_to be_nil
        expect(pix_row.occurred_on).to eq(Date.new(2025, 12, 31))
        expect(pix_row.amount).to eq(BigDecimal("-220.60"))
        expect(pix_row.description).not_to include("SALDO")

        rend_row = result.rows.find { |r| r.raw_line.include?("RENDPAGOAPLICAUTMAIS") && r.occurred_on == Date.new(2025, 12, 17) }
        expect(rend_row).not_to be_nil
        expect(rend_row.amount).to eq(BigDecimal("0.10"))
      end
    end

    it "levanta ParseError quando nenhuma linha reconhecida" do
      adapter = described_class.new(fake_pages("texto qualquer sem linhas de lançamento"))
      expect { adapter.parse }.to raise_error(PdfAdapters::ParseError)
    end

    it "gera warning para linha com data que não casa com o formato esperado, sem interromper o parsing" do
      page_text = <<~TEXT
        31/12/2025 valor sem formato numérico no final
        30/12/2025 PIXTRANSFTESTE30/12                                   -50,00
      TEXT
      adapter = described_class.new(fake_pages(page_text))

      result = adapter.parse

      expect(result.rows.size).to eq(1)
      expect(result.warnings.size).to eq(1)
      expect(result.warnings.first.reason).to include("não reconhecida")
    end
  end
end
