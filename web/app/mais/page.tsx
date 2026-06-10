import { PageHeader } from "@/components/ui/page-header"
import { EmptyState } from "@/components/ui/empty-state"

export default function Page() {
  return (
    <div className="p-4 md:p-6 max-w-5xl mx-auto">
      <PageHeader title="Mais" />
      <EmptyState title="Em construção" description="Esta página será implementada na Fase 2." />
    </div>
  )
}
