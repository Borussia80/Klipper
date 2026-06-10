import { PageHeader } from "@/components/ui/page-header"
import { KCard } from "@/components/ui/kcard"
import Link from "next/link"

const LINKS = [
  { href: "/investimentos", label: "Investimentos", icon: "📈", desc: "Carteira, FIIs, posições" },
  { href: "/kira",          label: "Kira IA",       icon: "🤖", desc: "Assistente financeiro" },
  { href: "/contas",        label: "Contas",         icon: "🏦", desc: "Contas bancárias e cartões" },
] as const

export default function MaisPage() {
  return (
    <div className="p-4 md:p-6 max-w-3xl mx-auto">
      <PageHeader title="Mais" />
      <div className="flex flex-col gap-2">
        {LINKS.map((l) => (
          <Link key={l.href} href={l.href}>
            <KCard variant="surface" className="flex items-center gap-4 hover:border-[var(--brass)] transition-colors cursor-pointer">
              <span className="text-2xl">{l.icon}</span>
              <div>
                <p className="text-sm font-medium text-[var(--ink)]">{l.label}</p>
                <p className="text-xs text-[var(--ink-3)]">{l.desc}</p>
              </div>
              <span className="ml-auto text-[var(--ink-4)]">›</span>
            </KCard>
          </Link>
        ))}
      </div>
    </div>
  )
}
