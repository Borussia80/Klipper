require "rails_helper"

RSpec.describe BankImport::FileGuard do
  describe ".ensure_valid!" do
    it "does not raise for a small CSV-looking file" do
      io = StringIO.new("Data,Descrição,Valor\n01/06/2026,teste,-10.00\n")

      expect { described_class.ensure_valid!(io, expected: :csv) }.not_to raise_error
    end

    it "does not raise for a small PDF-looking file" do
      io = StringIO.new("%PDF-1.4\n%âãÏÓ\n")

      expect { described_class.ensure_valid!(io, expected: :pdf) }.not_to raise_error
    end

    it "raises when a file bigger than the limit is sent" do
      io = StringIO.new("a" * (described_class::MAX_BYTES + 1))

      expect { described_class.ensure_valid!(io, expected: :csv) }
        .to raise_error(described_class::InvalidFile, /maior/)
    end

    it "raises when a PDF is uploaded to the CSV endpoint" do
      io = StringIO.new("%PDF-1.4\nconteudo binario")

      expect { described_class.ensure_valid!(io, expected: :csv) }
        .to raise_error(described_class::InvalidFile, /não parece ser um CSV/)
    end

    it "raises when a non-PDF file is uploaded to the PDF endpoint" do
      io = StringIO.new("Data,Descrição,Valor\n01/06/2026,teste,-10.00\n")

      expect { described_class.ensure_valid!(io, expected: :pdf) }
        .to raise_error(described_class::InvalidFile, /não é um PDF válido/)
    end

    it "leaves the file position at the start so the caller can still read it fully" do
      io = StringIO.new("Data,Descrição,Valor\n01/06/2026,teste,-10.00\n")

      described_class.ensure_valid!(io, expected: :csv)

      expect(io.read).to eq("Data,Descrição,Valor\n01/06/2026,teste,-10.00\n")
    end
  end
end
