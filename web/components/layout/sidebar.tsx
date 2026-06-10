"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { NAV_ITEMS } from "./nav-items"

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="hidden md:flex flex-col w-56 shrink-0 h-screen sticky top-0 bg-[var(--surface)] border-r border-[var(--rule)]">
      {/* Brand */}
      <div className="px-5 py-5 border-b border-[var(--rule)]">
        <span className="text-sm font-semibold text-[var(--brass)] tracking-wide">KLIPPER</span>
        <p className="text-[10px] text-[var(--ink-4)] mt-0.5">Wealth Operating System</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 flex flex-col gap-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href))
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                active
                  ? "bg-[var(--layer)] text-[var(--ink)] font-medium"
                  : "text-[var(--ink-3)] hover:text-[var(--ink)] hover:bg-[var(--layer)]"
              )}
            >
              <span className="w-5 text-center text-base">{item.icon}</span>
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* FAB secundário no desktop */}
      <div className="px-3 pb-5">
        <Link
          href="/transacoes/novo"
          className="flex items-center justify-center gap-2 w-full py-2 rounded-md bg-[var(--brass)] text-[var(--bg)] text-sm font-medium hover:opacity-90 transition-opacity"
        >
          + Lançamento
        </Link>
      </div>
    </aside>
  )
}
