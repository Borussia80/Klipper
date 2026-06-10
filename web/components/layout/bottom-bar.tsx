"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { NAV_ITEMS } from "./nav-items"

export function BottomBar() {
  const pathname = usePathname()

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-[var(--surface)] border-t border-[var(--rule)] flex items-stretch z-50">
      {/* Primeira metade (2 itens) */}
      {NAV_ITEMS.slice(0, 2).map((item) => (
        <BottomItem key={item.href} item={item} pathname={pathname} />
      ))}

      {/* FAB central */}
      <div className="flex items-center justify-center px-2">
        <Link
          href="/transacoes/novo"
          aria-label="Novo lançamento"
          className="flex items-center justify-center w-12 h-12 rounded-full bg-[var(--brass)] text-[var(--bg)] text-2xl font-light shadow-lg hover:opacity-90 transition-opacity touch-manipulation"
          style={{ minWidth: 44, minHeight: 44 }}
        >
          +
        </Link>
      </div>

      {/* Segunda metade (2 itens) */}
      {NAV_ITEMS.slice(2).map((item) => (
        <BottomItem key={item.href} item={item} pathname={pathname} />
      ))}
    </nav>
  )
}

function BottomItem({ item, pathname }: { item: (typeof NAV_ITEMS)[number]; pathname: string }) {
  const active = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href))

  return (
    <Link
      href={item.href}
      className={cn(
        "flex-1 flex flex-col items-center justify-center gap-0.5 text-[10px] transition-colors touch-manipulation",
        "min-h-[44px]",
        active ? "text-[var(--brass)]" : "text-[var(--ink-4)]"
      )}
    >
      <span className="text-lg leading-none">{item.icon}</span>
      <span>{item.label}</span>
    </Link>
  )
}
