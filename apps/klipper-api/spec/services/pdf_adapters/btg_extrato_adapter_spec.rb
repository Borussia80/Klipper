require "rails_helper"
require "pdf/reader"

RSpec.describe PdfAdapters::BtgExtratoAdapter do
  BtgFakePage = Struct.new(:text)
  NUL = [ "0000".to_i(16) ].pack("U")

  def fake_page(text)
    BtgFakePage.new(text)
  end

  def pages_for(path)
    PDF::Reader.new(path.to_s).pages
  end

  describe ".matches?" do
    it "reconhece marcadores de extrato BTG Pactual" do
      expect(described_class.matches?("... BTG PACTUAL SERVIÇOS ... Extrato da Conta Investimento ...")).to eq(true)
    end

    it "não reconhece texto de outro layout" do
      expect(described_class.matches?("agência:922conta:003163-8")).to eq(false)
      expect(described_class.matches?("... sua conta Nubank ... RESUMO DA FATURA ATUAL ...")).to eq(false)
    end
  end

  describe "#parse" do
    it "extrai lançamentos da seção Conta corrente - Movimentação e ignora saldo/total" do
      text = <<~TEXT
        Rend#{NUL} variável - Movimentação - Fundos Listados
         15/06/26           RENDIMENTO              XPLG11           FII        7         -            5,74             -            5,74
        Cont#{NUL} corrente - Movimentação
         01/06/26           Saldo Anterior                                                                                   0,02
         15/06/26           RENDIMENTOS - À VISTA s/ FII REC RECECI ER - RECR11                            1,11             1,13
         15/06/26           RENDIMENTOS - À VISTA s/ FII XP LOG CI - XPLG11                                5,74             6,87
         30/06/26           Saldo Final + Rendimento Provisionado de Saldo Remunerado                        -            33,06
         Total de                                                                                          33,04
         Débitos                                                                                              -
      TEXT

      result = described_class.new([ fake_page(text) ]).parse
      descriptions = result.rows.map(&:description)

      expect(descriptions).to contain_exactly(
        "RENDIMENTOS - À VISTA s/ FII REC RECECI ER - RECR11",
        "RENDIMENTOS - À VISTA s/ FII XP LOG CI - XPLG11"
      )

      first = result.rows.first
      expect(first.occurred_on).to eq(Date.new(2026, 6, 15))
      expect(first.amount).to eq(BigDecimal("1.11"))
      expect(first.saldo).to eq(BigDecimal("1.13"))
    end

    it "levanta ParseError quando nenhum lançamento é reconhecido" do
      text = <<~TEXT
        Cont#{NUL} corrente - Movimentação
        texto qualquer sem lançamento
      TEXT

      expect { described_class.new([ fake_page(text) ]).parse }.to raise_error(PdfAdapters::ParseError, /Nenhum lançamento/)
    end

    it "levanta ParseError quando a seção Conta corrente nunca aparece" do
      text = <<~TEXT
        Rend#{NUL} variável - Posição - Fundos Listados
         15/06/26           RENDIMENTOS - À VISTA s/ FII XP LOG CI - XPLG11                                5,74             6,87
      TEXT

      expect { described_class.new([ fake_page(text) ]).parse }.to raise_error(PdfAdapters::ParseError, /Nenhum lançamento/)
    end

    it "extrai lançamentos reais do extrato BTG" do
      with_pdf_fixture("btg_extrato.pdf") do |path|
        result = described_class.new(pages_for(path)).parse

        expect(result.rows.length).to eq(5)
        expect(result.rows.map(&:description)).to all(match(/RENDIMENTOS/))

        first = result.rows.first
        expect(first.occurred_on).to eq(Date.new(2026, 6, 15))
        expect(first.description).to eq("RENDIMENTOS - À VISTA s/ FII REC RECECI ER - RECR11")
        expect(first.amount).to eq(BigDecimal("1.11"))
        expect(first.saldo).to eq(BigDecimal("1.13"))

        last = result.rows.last
        expect(last.occurred_on).to eq(Date.new(2026, 6, 22))
        expect(last.amount).to eq(BigDecimal("15.39"))
        expect(last.saldo).to eq(BigDecimal("33.06"))
      end
    end
  end
end
