import { useQuery } from "@tanstack/react-query"
import { supabase } from "@/lib/supabase"
import type { Database } from "@/types/database"

type HealthProfessional = Database["public"]["Tables"]["health_professionals"]["Row"]

export function useHealthProfessionals() {
  return useQuery({
    queryKey: ["health-professionals"],
    queryFn: async (): Promise<HealthProfessional[]> => {
      const { data, error } = await supabase
        .from("health_professionals")
        .select("*")
        .eq("is_active", true)
        .order("name")
      if (error) throw error
      return data
    },
  })
}
