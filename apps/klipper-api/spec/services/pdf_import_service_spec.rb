require "rails_helper"

RSpec.describe PdfImportService do
  let(:user) { create(:user) }
  let(:account) { create(:account, user: user) }
  let(:service) { described_class.new(user, account_id: account.id) }

  describe "#preview" do
    it "retorna erro sem levantar exceção quando o PDF está corrompido/ilegível" do
      allow(PDF::Reader).to receive(:new).and_raise(PDF::Reader::MalformedPDFError, "não é PDF")

      result = service.preview(StringIO.new("não é um pdf de verdade"))

      expect(result.error?).to eq(true)
      expect(result.error).to match(/corrompido|ilegível/i)
    end

    it "retorna erro quando o PDF é válido mas o layout não é reconhecido por nenhum adapter" do
      fake_page = Struct.new(:text).new("um texto qualquer, sem nenhum marcador conhecido")
      fake_reader = instance_double(PDF::Reader, pages: [ fake_page ])
      allow(PDF::Reader).to receive(:new).and_return(fake_reader)

      result = service.preview(StringIO.new("qualquer coisa"))

      expect(result.error?).to eq(true)
      expect(result.error).to match(/não reconhecido/i)
      expect(result.rows).to eq([])
    end

    it "extrai e serializa lançamentos do extrato Itaú real" do
      with_pdf_fixture("itau_extrato.pdf") do |path|
        result = service.preview(File.open(path, "rb"))

        expect(result.error?).to eq(false)
        expect(result.adapter).to eq("itau_extrato")
        expect(result.rows).not_to be_empty

        row = result.rows.first
        expect(row[:occurred_on]).to match(/\A\d{4}-\d{2}-\d{2}\z/)
        expect(row[:amount]).to be_a(String)
        expect(row[:description]).to be_a(String)
        expect(row[:token]).to be_a(String)
      end
    end

    it "extrai e serializa lançamentos da fatura Itaú real" do
      with_pdf_fixture("itau_fatura.pdf") do |path|
        result = service.preview(File.open(path, "rb"))

        expect(result.error?).to eq(false)
        expect(result.adapter).to eq("itau_fatura")
        expect(result.rows).not_to be_empty
        expect(result.rows.first[:metadata]).to be_a(Hash)
      end
    end

    it "retorna erro sem levantar exceção quando o parsing do adapter encontra uma data inválida" do
      fake_page = Struct.new(:text).new("texto qualquer")
      fake_reader = instance_double(PDF::Reader, pages: [ fake_page ])
      allow(PDF::Reader).to receive(:new).and_return(fake_reader)

      adapter_class = double("FakeAdapter", adapter_key: "fake_adapter")
      allow(PdfAdapters::Registry).to receive(:detect).and_return(adapter_class)
      allow(adapter_class).to receive(:new).and_raise(Date::Error, "invalid date")

      result = service.preview(StringIO.new("qualquer coisa"))

      expect(result.error?).to eq(true)
      expect(result.error).to match(/não foi possível interpretar/i)
    end

    it "sugere o member_id do portador cujo nome normalizado bate com o cardholder" do
      member = create(:member, user: user, name: "Clarea Ana Almeida")
      fake_page = Struct.new(:text).new("texto qualquer")
      fake_reader = instance_double(PDF::Reader, pages: [ fake_page ])
      allow(PDF::Reader).to receive(:new).and_return(fake_reader)

      PdfAdapters::BaseAdapter
      row = PdfAdapters::Row.new(
        occurred_on: Date.new(2026, 6, 25), description: "Loja X", amount: BigDecimal("-10.00"),
        installment_number: nil, installment_total: nil, page: 1, raw_line: "",
        metadata: { cardholder: "CLAREAANAALMEIDA (final 7445)" }
      )
      parse_result = PdfAdapters::ParseResult.new(rows: [ row ], warnings: [])
      adapter_class = class_double("PdfAdapters::ItauFaturaAdapter", adapter_key: "itau_fatura").as_stubbed_const
      allow(PdfAdapters::Registry).to receive(:detect).and_return(adapter_class)
      allow(adapter_class).to receive(:new).and_return(instance_double(adapter_class, parse: parse_result))

      result = service.preview(StringIO.new("qualquer coisa"))

      expect(result.rows.first[:suggested_member_id]).to eq(member.id)
    end

    it "SEC-21: rejeita PDF com mais de 500 páginas" do
      many_pages = Array.new(501) { Struct.new(:text).new("page text") }
      fake_reader = instance_double(PDF::Reader, pages: many_pages)
      allow(PDF::Reader).to receive(:new).and_return(fake_reader)

      result = service.preview(StringIO.new("fake"))

      expect(result.error?).to eq(true)
      expect(result.error).to match(/páginas|limite|500/i)
    end

    it "SEC-21: aplica timeout na leitura do PDF e retorna erro claro" do
      allow(PDF::Reader).to receive(:new).and_raise(Timeout::Error, "execution expired")

      result = service.preview(StringIO.new("fake"))

      expect(result.error?).to eq(true)
      expect(result.error).to match(/tempo.*leitura|timeout/i)
    end

    it "sugere nil quando não há cardholder correspondente a nenhum portador" do
      fake_page = Struct.new(:text).new("texto qualquer")
      fake_reader = instance_double(PDF::Reader, pages: [ fake_page ])
      allow(PDF::Reader).to receive(:new).and_return(fake_reader)

      PdfAdapters::BaseAdapter
      row = PdfAdapters::Row.new(
        occurred_on: Date.new(2026, 6, 25), description: "Loja X", amount: BigDecimal("-10.00"),
        installment_number: nil, installment_total: nil, page: 1, raw_line: "",
        metadata: {}
      )
      parse_result = PdfAdapters::ParseResult.new(rows: [ row ], warnings: [])
      adapter_class = class_double("PdfAdapters::ItauFaturaAdapter", adapter_key: "itau_fatura").as_stubbed_const
      allow(PdfAdapters::Registry).to receive(:detect).and_return(adapter_class)
      allow(adapter_class).to receive(:new).and_return(instance_double(adapter_class, parse: parse_result))

      result = service.preview(StringIO.new("qualquer coisa"))

      expect(result.rows.first[:suggested_member_id]).to be_nil
    end
  end

  describe "#confirm" do
    it "persiste as linhas confirmadas como transações" do
      rows = [
        signed_row(occurred_on: "2026-06-25", description: "JoaoEMaria", amount: "-37.50"),
        signed_row(occurred_on: "2026-06-10", description: "LOJADOIS", amount: "-15.50")
      ]

      result = service.confirm(rows)

      expect(result.imported).to eq(2)
      expect(result.errors).to be_empty
      expect(user.transactions.count).to eq(2)
      expect(user.transactions.find_by(description: "JoaoEMaria").amount).to eq(BigDecimal("37.50"))
      expect(user.transactions.find_by(description: "JoaoEMaria").transaction_type).to eq("debit")
    end

    it "acumula erro por linha sem interromper as demais" do
      rows = [
        signed_row(occurred_on: "data-invalida", description: "RUIM", amount: "-10.00"),
        signed_row(occurred_on: "2026-06-10", description: "BOA", amount: "-15.50")
      ]

      result = service.confirm(rows)

      expect(result.imported).to eq(1)
      expect(result.errors.size).to eq(1)
      expect(user.transactions.count).to eq(1)
    end

    it "aceita installment_number/installment_total quando presentes" do
      rows = [
        signed_row(occurred_on: "2026-06-25", description: "PARCELADO", amount: "-100.00",
                   installment_number: 2, installment_total: 6)
      ]

      service.confirm(rows)

      tx = user.transactions.find_by(description: "PARCELADO")
      expect(tx.installment_number).to eq(2)
      expect(tx.installment_total).to eq(6)
    end

    it "não duplica quando a mesma linha é confirmada duas vezes" do
      rows = [
        signed_row(occurred_on: "2026-06-25", description: "JoaoEMaria", amount: "-37.50")
      ]

      service.confirm(rows)
      result = service.confirm(rows)

      expect(result.imported).to eq(0)
      expect(result.duplicates).to eq(1)
      expect(user.transactions.count).to eq(1)
    end

    it "reporta zero duplicatas na primeira confirmação" do
      rows = [ signed_row(occurred_on: "2026-06-25", description: "JoaoEMaria", amount: "-37.50") ]
      result = service.confirm(rows)
      expect(result.duplicates).to eq(0)
    end

    it "SEC-17: ignora um amount adulterado após o preview e persiste o valor assinado" do
      row = signed_row(occurred_on: "2026-06-25", description: "JoaoEMaria", amount: "-37.50")
      tampered = row.merge("amount" => "-999999.00")

      result = service.confirm([ tampered ])

      expect(result.imported).to eq(1)
      tx = user.transactions.find_by(description: "JoaoEMaria")
      expect(tx.amount).to eq(BigDecimal("37.50"))
    end

    it "SEC-17: ignora uma description adulterada após o preview e persiste o valor assinado" do
      row = signed_row(occurred_on: "2026-06-25", description: "JoaoEMaria", amount: "-37.50")
      tampered = row.merge("description" => "OUTRA COISA")

      result = service.confirm([ tampered ])

      expect(result.imported).to eq(1)
      expect(user.transactions.find_by(description: "JoaoEMaria")).to be_present
      expect(user.transactions.find_by(description: "OUTRA COISA")).to be_nil
    end

    it "SEC-17: ignora um occurred_on adulterado após o preview e persiste o valor assinado" do
      row = signed_row(occurred_on: "2026-06-25", description: "JoaoEMaria", amount: "-37.50")
      tampered = row.merge("occurred_on" => "2026-01-01")

      result = service.confirm([ tampered ])

      expect(result.imported).to eq(1)
      tx = user.transactions.find_by(description: "JoaoEMaria")
      expect(tx.occurred_on.iso8601).to eq("2026-06-25")
    end

    it "SEC-17: persiste os valores assinados no token, não os valores soltos reenviados no restante da row" do
      row = signed_row(occurred_on: "2026-06-25", description: "JoaoEMaria", amount: "-37.50")
      spoofed = row.merge("amount" => "-1.00", "description" => "FALSO")

      service.confirm([ spoofed ])

      tx = user.transactions.find_by(description: "JoaoEMaria")
      expect(tx).to be_present
      expect(tx.amount).to eq(BigDecimal("37.50"))
      expect(user.transactions.find_by(description: "FALSO")).to be_nil
    end

    it "SEC-17: acumula erro de linha quando o token está ausente, sem travar o lote" do
      rows = [
        { "occurred_on" => "2026-06-25", "description" => "SEM TOKEN", "amount" => "-10.00" },
        signed_row(occurred_on: "2026-06-10", description: "COM TOKEN", amount: "-15.50")
      ]

      result = service.confirm(rows)

      expect(result.imported).to eq(1)
      expect(result.errors.size).to eq(1)
      expect(user.transactions.find_by(description: "COM TOKEN")).to be_present
      expect(user.transactions.find_by(description: "SEM TOKEN")).to be_nil
    end

    it "SEC-17: em lote misto, processa as linhas com token válido e rejeita só a de token inválido" do
      valid_a = signed_row(occurred_on: "2026-06-25", description: "VALIDA A", amount: "-10.00")
      invalid_token = signed_row(occurred_on: "2026-06-25", description: "VALIDA B", amount: "-20.00")
                        .merge("token" => "token-forjado-invalido")
      valid_c = signed_row(occurred_on: "2026-06-25", description: "VALIDA C", amount: "-30.00")

      result = service.confirm([ valid_a, invalid_token, valid_c ])

      expect(result.imported).to eq(2)
      expect(result.errors.size).to eq(1)
      expect(user.transactions.count).to eq(2)
    end

    it "SEC-17: rejeita um token expirado" do
      row = signed_row(occurred_on: "2026-06-25", description: "JoaoEMaria", amount: "-37.50")

      result = travel(31.minutes) { service.confirm([ row ]) }

      expect(result.imported).to eq(0)
      expect(user.transactions.count).to eq(0)
    end

    it "SEC-23 (investigado e revertido): respeita o member_id escolhido pelo usuário na tela de confirmação" do
      chosen_member = create(:member, user: user, name: "Maria Clara")

      row = signed_row(occurred_on: "2026-06-25", description: "JoaoEMaria", amount: "-37.50")
      confirmed_by_user = row.merge("member_id" => chosen_member.id)

      result = service.confirm([ confirmed_by_user ])

      expect(result.imported).to eq(1)
      tx = user.transactions.find_by(description: "JoaoEMaria")
      expect(tx.member_id).to eq(chosen_member.id)
    end
  end
end
