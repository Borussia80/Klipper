module BankImport
  # Decide, pela descrição e pelo sinal, o kind de uma linha importada (spec 03,
  # L-12 e L-17). Os padrões de pagamento de fatura vêm de faturas e extratos
  # reais (Itaú, Nubank, Santander) e são estreitos de propósito: "FATURA CLARO"
  # e um PIX para alguém com conta no Nubank continuam sendo despesa. O extrato
  # do Itaú lido do PDF chega sem espaços ("PAGBOLETONUPAGAMENTOSSA"), por isso
  # os espaços são opcionais. Boleto pago a um banco sem marca de cartão
  # ("PAGBOLETOBANCOINTER") é ambíguo — pode ser empréstimo — e fica regular.
  # "Reembolso" fica de fora do estorno porque reembolso de plano é renda (L-18).
  class KindDetector
    CARD_PAYMENT = [
      /\Apagamento\s*(em|recebido|efetuado)\b/i,
      /\Apagamento\s*de\s*fatura\z/i,
      /fatura\s*paga/i,
      /pag\s*boleto\s*nu\s*pagamentos/i,
      /pag\s*boleto.*(visa|mastercard|amex)/i,
      /\bpag(to|amento)?\.?\s+(de\s+)?(fatura\s+)?(do\s+)?cart[aã]o\b/i
    ].freeze
    REFUND = /\bestorno\b|\bdevolu[cç][aã]o\b/i

    def self.call(description:, amount:)
      text = description.to_s.strip
      return "card_payment" if CARD_PAYMENT.any? { |re| re.match?(text) }
      return "refund" if amount.positive? && REFUND.match?(text)

      "regular"
    end
  end
end
