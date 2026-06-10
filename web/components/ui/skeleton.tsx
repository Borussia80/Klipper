import { cn } from "@/lib/utils"

interface SkeletonProps {
  className?: string
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn("animate-pulse rounded bg-[var(--layer)]", className)}
      aria-hidden="true"
    />
  )
}

export function SkeletonCard({ className }: SkeletonProps) {
  return (
    <div className={cn("rounded-[var(--radius)] bg-[var(--card)] p-4 space-y-3", className)}>
      <Skeleton className="h-3 w-24" />
      <Skeleton className="h-7 w-32" />
    </div>
  )
}

export function SkeletonRow() {
  return (
    <div className="flex items-center gap-3 px-4 py-3">
      <Skeleton className="h-5 w-20 shrink-0" />
      <Skeleton className="h-4 flex-1" />
      <Skeleton className="h-3 w-14 shrink-0" />
      <Skeleton className="h-4 w-20 shrink-0" />
    </div>
  )
}
