require "rails_helper"

RSpec.describe PdfAdapters::Registry do
  describe ".detect" do
    it "detecta o adapter de extrato pelo padrão agência/conta" do
      expect(described_class.detect("... agência:922conta:003163-8 ...")).to eq(PdfAdapters::ItauExtratoAdapter)
    end

    it "detecta o adapter de fatura pelo padrão de resumo da fatura" do
      expect(described_class.detect("... ResumodafaturaemR$ ...")).to eq(PdfAdapters::ItauFaturaAdapter)
    end

    it "detecta o adapter de fatura Nubank pelos marcadores nubank + resumo da fatura" do
      expect(described_class.detect("... sua conta Nubank ... RESUMO DA FATURA ATUAL ...")).to eq(PdfAdapters::NubankFaturaAdapter)
    end

    it "detecta o adapter de extrato BTG pelos marcadores BTG Pactual + investimento" do
      expect(described_class.detect("... BTG PACTUAL SERVIÇOS ... Extrato da Conta Investimento ...")).to eq(PdfAdapters::BtgExtratoAdapter)
    end

    it "detecta o adapter de extrato Santander sem alterar a detecção dos layouts existentes" do
      santander = "EXTRATO DE CONTA\nAgência: 1234 | Conta: 12.345678.9\nDETALHE DOS MOVIMENTOS"

      expect(described_class.detect(santander)).to eq(PdfAdapters::SantanderExtratoAdapter)
      expect(described_class.detect("... agência:922conta:003163-8 ...")).to eq(PdfAdapters::ItauExtratoAdapter)
      expect(described_class.detect("... ResumodafaturaemR$ ...")).to eq(PdfAdapters::ItauFaturaAdapter)
      expect(described_class.detect("... sua conta Nubank ... RESUMO DA FATURA ATUAL ...")).to eq(PdfAdapters::NubankFaturaAdapter)
      expect(described_class.detect("... BTG PACTUAL SERVIÇOS ... Extrato da Conta Investimento ...")).to eq(PdfAdapters::BtgExtratoAdapter)
    end

    it "retorna nil quando nenhum adapter reconhece o texto" do
      expect(described_class.detect("texto de um layout desconhecido, sem marcadores")).to be_nil
    end
  end
end
