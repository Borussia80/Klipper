export const NAV_ITEMS = [
  { href: "/",              label: "Home",         icon: "🏠" },
  { href: "/transacoes",    label: "Transações",   icon: "↕" },
  { href: "/contas",        label: "Contas",       icon: "🏦" },
  { href: "/orcamento",     label: "Orçamento",    icon: "◎" },
  { href: "/saude",         label: "Saúde",        icon: "❤" },
  { href: "/investimentos", label: "Investimentos",icon: "📈" },
  { href: "/mais",          label: "Mais",         icon: "⋯" },
] as const

export type NavItem = (typeof NAV_ITEMS)[number]
