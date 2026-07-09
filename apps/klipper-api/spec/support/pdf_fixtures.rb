module PdfFixtures
  DIR = Rails.root.join("spec", "fixtures", "pdf")

  def pdf_fixture_path(filename)
    DIR.join(filename)
  end

  def with_pdf_fixture(filename)
    path = pdf_fixture_path(filename)
    unless File.exist?(path)
      skip "PDF fixture '#{filename}' não está presente localmente (gitignored, dados bancários " \
           "reais) — copie de Modelo_Bancos/ para spec/fixtures/pdf/ para rodar este spec " \
           "(veja spec/fixtures/pdf/README.md)."
    end
    yield path
  end
end

RSpec.configure { |c| c.include PdfFixtures }
