require "rails_helper"

RSpec.describe PdfAdapters::SantanderExtratoAdapter do
  SantanderFakePage = Struct.new(:text)

  def fake_pages(*texts)
    texts.map { |text| SantanderFakePage.new(text) }
  end

  def statement_pages(final_balance: "1.500,00")
    [
      <<~TEXT,
        EXTRATO DE CONTA
        Agência: 1234 | Conta: 12.345678.9
        Período: 10/10/2026  a  13/10/2026
        Titular: Cliente Exemplo
          Saldo inicial                   Entradas                        Saídas                         Saldo final
          R$ 1.000,00                     R$ 700,00                       R$ 200,00                     R$ #{final_balance}
        DETALHE DOS MOVIMENTOS
        Data              Descrição                                                                     Valor                Saldo
         Terça, 13 de outubro de 2026
                          Pix enviado open finance
        13/10/2026                                                                                    -R$ 50,00          R$ 1.500,00
                          ANA FICTICIA LTDA
                          Pix recebido
        13/10/2026                                                                                     R$ 200,00          R$ 1.550,00
                          BETA SERVICOS SA
         Segunda, 12 de outubro de 2026
        12/10/2026        Resgate/CDB                                                              R$ 0,00          R$ 1.350,00
      TEXT
      <<~TEXT
        DETALHE DOS MOVIMENTOS
        Data              Descrição                                                                     Valor                Saldo
         Domingo, 11 de outubro de 2026
                          Compra mercado
        11/10/2026                                                                                    -R$ 150,00         R$ 1.350,00
                          MERCADO IMAGINARIO
                          Pix recebido salario
        11/10/2026                                                                                     R$ 400,00          R$ 1.450,00
                          EMPRESA FICTICIA
         Sábado, 10 de outubro de 2026
                          Deposito em dinheiro
        10/10/2026                                                                                     R$ 100,00          R$ 1.100,00
                          CAIXA AGENCIA TESTE
        2/2
      TEXT
    ]
  end

  describe ".matches?" do
    it "reconhece somente o layout de extrato de conta Santander" do
      expect(described_class.matches?(statement_pages.join("\n"))).to eq(true)
      expect(described_class.matches?("EXTRATO DE CONTA\nDETALHE DOS MOVIMENTOS")).to eq(false)
      expect(described_class.matches?("Agência: 1234\nDETALHE DOS MOVIMENTOS")).to eq(false)
    end

    it "reconhece o título mesmo quando o PDF perde o espaço entre as palavras (EXTRATODE CONTA)" do
      text = "EXTRATODE CONTA\nAgência: 1234 | Conta: 12.345678.9\nDETALHE DOS MOVIMENTOS"

      expect(described_class.matches?(text)).to eq(true)
    end
  end

  describe "#parse" do
    it "normaliza movimentos de duas páginas, inclusive descrição inline, saldos e contraparte" do
      result = described_class.new(fake_pages(*statement_pages)).parse

      expect(result.rows.size).to eq(6)
      expect(result.rows.map(&:page)).to eq([ 1, 1, 1, 2, 2, 2 ])
      expect(result.rows.map(&:amount)).to eq([
        BigDecimal("-50.00"), BigDecimal("200.00"), BigDecimal("0.00"),
        BigDecimal("-150.00"), BigDecimal("400.00"), BigDecimal("100.00")
      ])
      expect(result.rows.map(&:occurred_on)).to include(Date.new(2026, 10, 13), Date.new(2026, 10, 10))
      expect(result.rows.first.description).to eq("Pix enviado open finance ANA FICTICIA LTDA")
      expect(result.rows[2].description).to eq("Resgate/CDB")
      expect(result.rows[2].metadata[:balance]).to eq(BigDecimal("1350.00"))
      expect(result.rows.first.metadata[:statement_closing_balance]).to eq(BigDecimal("1500.00"))
      expect(result.rows.drop(1).none? { |row| row.metadata.key?(:statement_closing_balance) }).to eq(true)
      expect(result.warnings).to be_empty
    end

    it "emite warning, sem erro, quando o quadro de saldos não reconcilia" do
      result = described_class.new(fake_pages(*statement_pages(final_balance: "1.499,00"))).parse

      expect(result.warnings).to include(have_attributes(
        reason: /saldo inicial.*saldo final/i,
        raw_text: include("1.499,00")
      ))
    end

    it "ignora cabeçalhos e rodapé e falha quando não há movimentos reconhecíveis" do
      text = <<~TEXT
        EXTRATO DE CONTA
        Agência: 1234 | Conta: 12.345678.9
        DETALHE DOS MOVIMENTOS
        Data              Descrição                                                                     Valor                Saldo
        Terça, 13 de outubro de 2026
        1/1
      TEXT

      expect { described_class.new(fake_pages(text)).parse }.to raise_error(PdfAdapters::ParseError, /Nenhum lançamento/)
    end

    it "lê o quadro de saldos mesmo com a ligatura 'ﬁ' em 'Saldo ﬁnal' (como no PDF real)" do
      pages = statement_pages.map { |text| text.sub("Saldo final", "Saldo \uFB01nal") }

      result = described_class.new(fake_pages(*pages)).parse

      expect(result.rows.first.metadata[:statement_closing_balance]).to eq(BigDecimal("1500.00"))
    end

    it "lê o quadro de saldos com espaço não separável depois de 'R$' (como no PDF real)" do
      pages = statement_pages.map { |text| text.gsub("R$ ", "R$\u00A0") }

      result = described_class.new(fake_pages(*pages)).parse

      expect(result.rows.first.metadata[:statement_closing_balance]).to eq(BigDecimal("1500.00"))
      expect(result.rows.size).to eq(statement_pages.sum { |t| t.scan(/\d{2}\/\d{2}\/\d{4}\s+.*R\$/).size })
    end
  end
end
