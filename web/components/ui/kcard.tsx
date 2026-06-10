import { cn } from "@/lib/utils"
import type { HTMLAttributes } from "react"

interface KCardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "surface" | "layer"
  padding?: "none" | "sm" | "md" | "lg"
}

export function KCard({ variant = "default", padding = "md", className, children, ...props }: KCardProps) {
  return (
    <div
      className={cn(
        "rounded-lg border",
        {
          "bg-[var(--card)] border-[var(--rule)] shadow-[var(--shadow-card)]": variant === "default",
          "bg-[var(--surface)] border-[var(--rule)]": variant === "surface",
          "bg-[var(--layer)] border-[var(--rule)]": variant === "layer",
        },
        {
          "p-0": padding === "none",
          "p-3": padding === "sm",
          "p-4": padding === "md",
          "p-6": padding === "lg",
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
