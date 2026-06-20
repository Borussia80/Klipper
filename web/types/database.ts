// Auto-gerado do schema Supabase (migrations 001–005b)
// Atualizado manualmente para migrações 006–007 (is_recurring, transaction_splits).
// Módulo Saúde removido: reembolsos do Pedro vivem no projeto Gestor-Reembolsos (desktop).
// Regenerar após próximas migrations: npx supabase gen types typescript --linked > types/database.ts

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
          status: "PAGO" | "PENDENTE" | "AGENDADO" | "PENDENTE_SYNC"
          is_recurring: boolean
          user_id: string
          created_at: string
        }
        Insert: {
          id?: string
          date: string
          amount: number
          type: "GASTO" | "GANHO"
          category: string
          notes?: string
          payment_method: "PIX" | "CARTAO_CREDITO" | "CARTAO_DEBITO" | "DINHEIRO" | "TED" | "BOLETO" | "TRANSFERENCIA"
          account_id?: string | null
          card_id?: string | null
          installment_id?: string | null
          status?: "PAGO" | "PENDENTE" | "AGENDADO"
          is_recurring?: boolean
          user_id?: string
          created_at?: string
        }
        Update: {
          id?: string
          date?: string
          amount?: number
          type?: "GASTO" | "GANHO"
          category?: string
          notes?: string
          payment_method?: "PIX" | "CARTAO_CREDITO" | "CARTAO_DEBITO" | "DINHEIRO" | "TED" | "BOLETO" | "TRANSFERENCIA"
          account_id?: string | null
          card_id?: string | null
          installment_id?: string | null
          status?: "PAGO" | "PENDENTE" | "AGENDADO"
          is_recurring?: boolean
          user_id?: string
          created_at?: string
        }
        Relationships: []
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
        Insert: {
          id?: string
          name: string
          bank: string
          type: "CORRENTE" | "POUPANCA" | "INVESTIMENTO"
          balance: number
          color?: string
          is_active?: boolean
          user_id?: string
          created_at?: string
        }
        Update: {
          id?: string
          name?: string
          bank?: string
          type?: "CORRENTE" | "POUPANCA" | "INVESTIMENTO"
          balance?: number
          color?: string
          is_active?: boolean
          user_id?: string
          created_at?: string
        }
        Relationships: []
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
        Insert: {
          id?: string
          name: string
          bank: string
          limit_total: number
          closing_day: number
          due_day: number
          color?: string
          is_active?: boolean
          user_id?: string
          created_at?: string
        }
        Update: {
          id?: string
          name?: string
          bank?: string
          limit_total?: number
          closing_day?: number
          due_day?: number
          color?: string
          is_active?: boolean
          user_id?: string
          created_at?: string
        }
        Relationships: []
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
        Insert: {
          id?: string
          category: string
          monthly_limit: number
          year: number
          month: number
          user_id?: string
          created_at?: string
        }
        Update: {
          id?: string
          category?: string
          monthly_limit?: number
          year?: number
          month?: number
          user_id?: string
          created_at?: string
        }
        Relationships: []
      }
      investments: {
        Row: {
          id: string
          ticker: string
          type: "FII" | "Ação" | "Renda Fixa" | "Caixa"
          quantity: number
          avg_price: number
          current_price: number
          dy_12m: number
          pvp: number
          liquidity_daily: number
          volatility: number
          spread_vs_cdi: number
          sector: string
          fragility_score: number
          notes: string
          user_id: string
          updated_at: string
        }
        Insert: {
          id?: string
          ticker: string
          type: "FII" | "Ação" | "Renda Fixa" | "Caixa"
          quantity: number
          avg_price: number
          current_price: number
          dy_12m?: number
          pvp?: number
          liquidity_daily?: number
          volatility?: number
          spread_vs_cdi?: number
          sector?: string
          fragility_score?: number
          notes?: string
          user_id?: string
          updated_at?: string
        }
        Update: {
          id?: string
          ticker?: string
          type?: "FII" | "Ação" | "Renda Fixa" | "Caixa"
          quantity?: number
          avg_price?: number
          current_price?: number
          dy_12m?: number
          pvp?: number
          liquidity_daily?: number
          volatility?: number
          spread_vs_cdi?: number
          sector?: string
          fragility_score?: number
          notes?: string
          user_id?: string
          updated_at?: string
        }
        Relationships: []
      }
      categorization_rules: {
        Row: {
          id:         string
          priority:   number
          field:      "notes" | "amount"
          operator:   "contains" | "starts_with" | "equals" | "greater_than" | "less_than" | "regex"
          value:      string
          category:   string
          is_active:  boolean
          user_id:    string
          created_at: string
        }
        Insert: {
          id?:        string
          priority?:  number
          field:      "notes" | "amount"
          operator:   "contains" | "starts_with" | "equals" | "greater_than" | "less_than" | "regex"
          value:      string
          category:   string
          is_active?: boolean
          user_id?:   string
          created_at?: string
        }
        Update: {
          id?:        string
          priority?:  number
          field?:     "notes" | "amount"
          operator?:  "contains" | "starts_with" | "equals" | "greater_than" | "less_than" | "regex"
          value?:     string
          category?:  string
          is_active?: boolean
          user_id?:   string
          created_at?: string
        }
        Relationships: []
      }
      }
  Views: { [_ in never]: never }
    Functions: { [_ in never]: never }
    Enums: { [_ in never]: never }
    CompositeTypes: { [_ in never]: never }
  }
}
