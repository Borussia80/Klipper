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

      category = find_category(user, rule[:name])
      return category if category
    end
    nil
  end

  # A regra procura a categoria pelo nome. Se ela foi mesclada em outra, o nome
  # aponta para uma categoria inativa e a regra pararia de acertar; seguir
  # merged_into_id leva ao destino da mesclagem.
  MAX_MERGE_HOPS = 5

  def self.find_category(user, name)
    category = user.categories.active.find_by(name: name) ||
      user.categories.where(active: false).where.not(merged_into_id: nil).find_by(name: name)

    MAX_MERGE_HOPS.times do
      break if category.nil? || category.active

      category = category.merged_into
    end

    category&.active ? category : nil
  end
  private_class_method :find_category
end
