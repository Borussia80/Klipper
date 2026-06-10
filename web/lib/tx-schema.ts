import { z } from "zod"

export const CATEGORIES_GASTO = [
  "Moradia", "Alimentação", "Transporte", "Saúde",
  "Educação", "Lazer", "Investimento", "Outros",
] as const

export const CATEGORIES_GANHO = ["Renda", "Freelance", "Outros"] as const

export const PAYMENT_METHODS = [
  { value: "PIX",            label: "PIX" },
  { value: "CARTAO_CREDITO", label: "Cartão Crédito" },
  { value: "CARTAO_DEBITO",  label: "Cartão Débito" },
  { value: "DINHEIRO",       label: "Dinheiro" },
  { value: "TED",            label: "TED" },
  { value: "BOLETO",         label: "Boleto" },
  { value: "TRANSFERENCIA",  label: "Transferência" },
] as const

export const CAT_COLORS: Record<string, string> = {
  Moradia:       "#6366F1",
  Alimentação:   "#F59E0B",
  Transporte:    "#3B82F6",
  Saúde:         "#10B981",
  Educação:      "#8B5CF6",
  Lazer:         "#EC4899",
  Investimento:  "#D9B26F",
  Renda:         "#10B981",
  Freelance:     "#34D399",
  Outros:        "#94A3B8",
}

export const txSchema = z.object({
  date:           z.string().min(1, "Data obrigatória"),
  amount:         z.coerce.number().positive("Valor deve ser positivo"),
  type:           z.enum(["GASTO", "GANHO"]),
  category:       z.string().min(1, "Categoria obrigatória"),
  notes:          z.string().optional().default(""),
  payment_method: z.enum([
    "PIX", "CARTAO_CREDITO", "CARTAO_DEBITO",
    "DINHEIRO", "TED", "BOLETO", "TRANSFERENCIA",
  ]),
  status:         z.enum(["PAGO", "PENDENTE", "AGENDADO"]).default("PAGO"),
  account_id:     z.string().uuid().nullable().optional(),
  card_id:        z.string().uuid().nullable().optional(),
})

export type TxFormValues = z.infer<typeof txSchema>
