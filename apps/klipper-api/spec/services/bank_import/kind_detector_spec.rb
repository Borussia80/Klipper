require "rails_helper"

# D1 (spec 03, L-12 e L-17): o que a importação reconhece como pagamento de
# fatura e como estorno. Os formatos vêm de extratos e faturas reais (Itaú,
# Nubank); os valores são sintéticos.
RSpec.describe BankImport::KindDetector do
  def kind(description, amount)
    described_class.call(description: description, amount: BigDecimal(amount.to_s))
  end

  context "pagamento de fatura" do
    it "linha de pagamento na própria fatura" do
      expect(kind("Pagamento em 10 JUN", 160)).to eq("card_payment")
      expect(kind("PAGAMENTO EFETUADO", 900)).to eq("card_payment")
    end

    it "linhas do extrato da conta corrente" do
      expect(kind("FATURA PAGA PERSONNALITE", -5000)).to eq("card_payment")
      expect(kind("PAG BOLETO NU PAGAMENTOS SA", -320)).to eq("card_payment")
      expect(kind("Pagamento de fatura", -320)).to eq("card_payment")
      expect(kind("PAGTO CARTAO CREDITO", -320)).to eq("card_payment")
    end

    it "extrato do Itaú lido do PDF, sem espaços" do
      expect(kind("FATURAPAGAPERSONNALITE", -5000)).to eq("card_payment")
      expect(kind("PAGBOLETONUPAGAMENTOSSA", -320)).to eq("card_payment")
      expect(kind("PAGBOLETOSANTANDERFREEVISA-1234", -410)).to eq("card_payment")
    end

    it "boleto a banco sem marca de cartão é ambíguo e fica regular" do
      expect(kind("PAGBOLETOBANCOINTER", -500)).to eq("regular")
      expect(kind("PAGBOLETOITAUUNIBANCOHOLDINGS.A.", -500)).to eq("regular")
      expect(kind("PAGBOLETORAPIDANETTELECOMLTDA", -99)).to eq("regular")
    end

    it "não confunde conta de consumo, salário nem PIX para terceiros" do
      expect(kind("PAGAMENTO SALARIO", 5000)).to eq("regular")
      expect(kind("FATURA CLARO", -120)).to eq("regular")
      expect(kind("PIX ENVIADO FULANO NU PAGAMENTOS", -50)).to eq("regular")
      expect(kind("PAG BOLETO ENEL", -210)).to eq("regular")
    end
  end

  context "estorno" do
    it "crédito com estorno ou devolução" do
      expect(kind("ESTORNO COMPRA LOJA X", 59.9)).to eq("refund")
      expect(kind("Devolução de compra", 30)).to eq("refund")
    end

    it "débito com a palavra não é estorno" do
      expect(kind("ESTORNO TARIFA COBRADA", -10)).to eq("regular")
    end

    # Reembolso de plano de saúde é renda (L-18), não estorno do estabelecimento.
    it "reembolso de terceiro continua regular" do
      expect(kind("REEMBOLSO SULAMERICA", 300)).to eq("regular")
    end
  end
end
