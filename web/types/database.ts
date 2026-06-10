// Auto-gerado do schema Supabase (migrations 001–005b)
// Regenerar após migrations: npx supabase gen types typescript --linked > types/database.ts

export type Json = string | number | boolean | null | { [key: string]: Json } | Json[]

export interface Database {
  public: {
    Tables: {
      transactions: {
        Row: {
          id: string
          date: string
          amount: number
          type: "GASTO" | "GANHO"
          category: string
          notes: string
          payment_method: "PIX" | "CARTAO_CREDITO" | "CARTAO_DEBITO" | "DINHEIRO" | "TED" | "BOLETO" | "TRANSFERENCIA"
          account_id: string | null
          card_id: string | null
          installment_id: string | null
          status: "PAGO" | "PENDENTE" | "AGENDADO"
          user_id: string
          created_at: string
        }
        Insert: Omit<Database["public"]["Tables"]["transactions"]["Row"], "id" | "created_at"> & {
          id?: string
          created_at?: string
        }
        Update: Partial<Database["public"]["Tables"]["transactions"]["Insert"]>
      }
      bank_accounts: {
        Row: {
          id: string
          name: string
          bank: string
          type: "CORRENTE" | "POUPANCA" | "INVESTIMENTO"
          balance: number
          color: string
          is_active: boolean
          user_id: string
          created_at: string
        }
        Insert: Omit<Database["public"]["Tables"]["bank_accounts"]["Row"], "id" | "created_at"> & {
          id?: string
          created_at?: string
        }
        Update: Partial<Database["public"]["Tables"]["bank_accounts"]["Insert"]>
      }
      credit_cards: {
        Row: {
          id: string
          name: string
          bank: string
          limit_total: number
          closing_day: number
          due_day: number
          color: string
          is_active: boolean
          user_id: string
          created_at: string
        }
        Insert: Omit<Database["public"]["Tables"]["credit_cards"]["Row"], "id" | "created_at"> & {
          id?: string
          created_at?: string
        }
        Update: Partial<Database["public"]["Tables"]["credit_cards"]["Insert"]>
      }
      budgets: {
        Row: {
          id: string
          category: string
          monthly_limit: number
          year: number
          month: number
          user_id: string
          created_at: string
        }
        Insert: Omit<Database["public"]["Tables"]["budgets"]["Row"], "id" | "created_at"> & {
          id?: string
          created_at?: string
        }
        Update: Partial<Database["public"]["Tables"]["budgets"]["Insert"]>
      }
      health_professionals: {
        Row: {
          id: string
          name: string
          specialty: "FONOAUDIOLOGIA" | "TERAPIA_OCUPACIONAL" | "PSICOLOGIA" | "PSIQUIATRIA" | "NEUROLOGIA" | "FISIOTERAPIA" | "OUTRO"
          council_number: string | null
          is_active: boolean
          user_id: string
          created_at: string
        }
        Insert: Omit<Database["public"]["Tables"]["health_professionals"]["Row"], "id" | "created_at"> & {
          id?: string
          created_at?: string
        }
        Update: Partial<Database["public"]["Tables"]["health_professionals"]["Insert"]>
      }
    }
    Views: Record<string, never>
    Functions: Record<string, never>
    Enums: Record<string, never>
  }
}
