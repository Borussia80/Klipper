export const NAV_ITEMS = [
  { href: "/",              label: "Home",         icon: "🏠" },
  { href: "/transacoes",    label: "Transações",   icon: "↕" },
  { href: "/investimentos", label: "Investimentos",icon: "📈" },
  { href: "/mais",          label: "Mais",         icon: "⋯" },
] as const

export type NavItem = (typeof NAV_ITEMS)[number]
