class AutoCategorizerService
  RULES = [
    { pattern: /supermercado|mercadão|pão de açúcar|extra\b|carrefour|walmart|assaí|atacadão/i, name: "Alimentação" },
    { pattern: /ifood|rappi|uber.?eats|delivery|restaurante|lanchonete|padaria|açougue/i, name: "Alimentação" },
    { pattern: /uber\b|99pop|cabify|taxi|gasolina|combustível|posto\b|shell\b|ipiranga/i, name: "Transporte" },
    { pattern: /netflix|spotify|amazon.?prime|deezer|globoplay|hbo|disney/i, name: "Lazer" },
    { pattern: /farmácia|drogasil|droga raia|ultrafarma|panvel|médico|hospital|clínica/i, name: "Saúde" },
    { pattern: /aluguel|condomínio|iptu|energia|enel|cemig|sabesp/i, name: "Moradia" },
    { pattern: /salário|pagamento|vencimento|folha/i, name: "Renda" },
    { pattern: /escola|faculdade|curso|mensalidade|udemy|coursera/i, name: "Educação" }
  ].freeze

  def self.call(description, user)
    RULES.each do |rule|
      next unless rule[:pattern].match?(description)

      category = user.categories.active.find_by(name: rule[:name])
      return category if category
    end
    nil
  end
end
