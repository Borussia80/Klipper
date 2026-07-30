# Fixtures de PDF (locais, não versionadas)

Os arquivos `.pdf` nesta pasta são gitignored (contêm dados financeiros pessoais reais) e
precisam ser copiados manualmente para rodar os specs de adapter/`PdfImportService` localmente.

Copie de `Modelo_Bancos/` (raiz do repo) para cá com estes nomes exatos:

| Arquivo esperado aqui | Origem em `Modelo_Bancos/` |
|---|---|
| `itau_extrato.pdf` | `itau_extrato_072025.pdf` |
| `itau_fatura.pdf`  | `Extrato_Cartão_Itau_Personnalite.pdf` |
| `nubank_fatura.pdf` | `Nubank_2026-07-10.pdf` |
| `btg_extrato.pdf` | `report_146828241.pdf` |

Specs que dependem desses arquivos usam o helper `with_pdf_fixture` (`spec/support/pdf_fixtures.rb`)
e são automaticamente puladas (`skip`), com mensagem explicando o motivo, em qualquer máquina/CI
onde os arquivos não estejam presentes — nunca falham silenciosamente nem passam por engano.
