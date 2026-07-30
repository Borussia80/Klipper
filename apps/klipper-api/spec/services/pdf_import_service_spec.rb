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
        { "occurred_on" => "2026-06-25", "description" => "JoaoEMaria", "amount" => "-37.50" },
        { "occurred_on" => "2026-06-10", "description" => "LOJADOIS", "amount" => "-15.50" }
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
        { "occurred_on" => "data-invalida", "description" => "RUIM", "amount" => "-10.00" },
        { "occurred_on" => "2026-06-10", "description" => "BOA", "amount" => "-15.50" }
      ]

      result = service.confirm(rows)

      expect(result.imported).to eq(1)
      expect(result.errors.size).to eq(1)
      expect(user.transactions.count).to eq(1)
    end

    it "aceita installment_number/installment_total quando presentes" do
      rows = [
        { "occurred_on" => "2026-06-25", "description" => "PARCELADO", "amount" => "-100.00",
          "installment_number" => 2, "installment_total" => 6 }
      ]

      service.confirm(rows)

      tx = user.transactions.find_by(description: "PARCELADO")
      expect(tx.installment_number).to eq(2)
      expect(tx.installment_total).to eq(6)
    end

    it "não duplica quando a mesma linha é confirmada duas vezes" do
      rows = [
        { "occurred_on" => "2026-06-25", "description" => "JoaoEMaria", "amount" => "-37.50" }
      ]

      service.confirm(rows)
      result = service.confirm(rows)

      expect(result.imported).to eq(0)
      expect(result.duplicates).to eq(1)
      expect(user.transactions.count).to eq(1)
    end

    it "reporta zero duplicatas na primeira confirmação" do
      rows = [{ "occurred_on" => "2026-06-25", "description" => "JoaoEMaria", "amount" => "-37.50" }]
      result = service.confirm(rows)
      expect(result.duplicates).to eq(0)
    end
  end
end
