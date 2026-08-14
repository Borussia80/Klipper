module BankImport
  class FileGuard
    class InvalidFile < StandardError; end

    MAX_BYTES = 10.megabytes
    PDF_MAGIC = "%PDF-".b

    def self.ensure_valid!(file_io, expected:)
      new(file_io, expected: expected).ensure_valid!
    end

    def initialize(file_io, expected:)
      @file_io = file_io
      @expected = expected
    end

    def ensure_valid!
      ensure_size!
      ensure_magic_bytes!
    end

    private

    def ensure_size!
      size = @file_io.respond_to?(:size) ? @file_io.size.to_i : header_bytes.bytesize
      raise InvalidFile, "Arquivo maior que #{MAX_BYTES / 1.megabyte}MB" if size > MAX_BYTES
    end

    def ensure_magic_bytes!
      is_pdf = header_bytes.start_with?(PDF_MAGIC)

      case @expected
      when :pdf
        raise InvalidFile, "Arquivo não é um PDF válido" unless is_pdf
      when :csv
        raise InvalidFile, "Arquivo não parece ser um CSV de texto" if is_pdf
      end
    end

    def header_bytes
      return @header_bytes if defined?(@header_bytes)

      @file_io.rewind if @file_io.respond_to?(:rewind)
      @header_bytes = @file_io.read(5).to_s.b
      @file_io.rewind if @file_io.respond_to?(:rewind)
      @header_bytes
    end
  end
end
