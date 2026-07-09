class DefaultCategoriesSeederService
  DEFAULTS = [
    { name: "Alimentação",    category_type: "expense",  natureza: "variavel", icon: "alimentacao",   color: "#E59010" },
    { name: "Transporte",     category_type: "expense",  natureza: "variavel", icon: "transporte",    color: "#2B7DF4" },
    { name: "Moradia",        category_type: "expense",  natureza: "fixo",     icon: "moradia",       color: "#7C5CF5" },
    { name: "Saúde",          category_type: "expense",  natureza: "variavel", icon: "saude",         color: "#E83535" },
    { name: "Educação",       category_type: "expense",  natureza: "fixo",     icon: "educacao",      color: "#0DB878" },
    { name: "Lazer",          category_type: "expense",  natureza: "variavel", icon: "lazer",         color: "#F4C030" },
    { name: "Outros",         category_type: "expense",  natureza: "variavel", icon: "wallet",        color: "#6B93AE" },
    { name: "Renda",          category_type: "income",   natureza: "variavel", icon: "renda",         color: "#0DB878" },
    { name: "Transferência",  category_type: "transfer", natureza: "variavel", icon: "transferencia", color: "#6B93AE" }
  ].freeze

  def self.call(user)
    DEFAULTS.each do |attrs|
      next if user.categories.exists?(name: attrs[:name])

      user.categories.create!(attrs)
    end
  end
end
