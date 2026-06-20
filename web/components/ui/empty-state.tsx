import { cn } from "@/lib/utils"
import type { ReactNode } from "react"

interface EmptyStateProps {
  icon?:        ReactNode
  title:        string
  description?: string
  action?:      ReactNode
  className?:   string
}

export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 py-16 text-center animate-fade-up",
        className,
      )}
    >
      {icon && (
        <div className="w-14 h-14 rounded-full bg-[var(--surface)] flex items-center justify-center text-2xl text-[var(--ink-4)]">
          {icon}
        </div>
      )}
      <p className="text-sm font-medium text-[var(--ink-3)]">{title}</p>
      {description && (
        <p className="text-xs text-[var(--ink-4)] max-w-[240px] leading-relaxed">{description}</p>
      )}
      {action && <div className="mt-2">{action}</div>}
    </div>
  )
}
