module BankImport
  # Assina/verifica os campos financeiros de uma linha de importação de PDF, para que
  # imports_controller#confirm nunca persista amount/description/occurred_on vindos
  # direto do cliente sem vínculo ao que #preview extraiu do documento original.
  class RowSigner
    class InvalidSignature < StandardError; end

    PURPOSE = :bank_import_row
    TTL = 30.minutes

    def self.sign(canonical_row)
      verifier.generate(canonical_row.stringify_keys, purpose: PURPOSE, expires_in: TTL)
    end

    def self.verify!(token)
      raise InvalidSignature, "Assinatura da linha ausente" if token.blank?

      verifier.verify(token, purpose: PURPOSE).with_indifferent_access
    rescue ActiveSupport::MessageVerifier::InvalidSignature
      raise InvalidSignature, "Assinatura da linha inválida ou expirada — refaça o preview"
    end

    def self.verifier
      Rails.application.message_verifier(PURPOSE)
    end
    private_class_method :verifier
  end
end
