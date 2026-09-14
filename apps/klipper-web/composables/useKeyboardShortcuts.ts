/**
 * Mapeamento centralizado de atalhos globais de teclado do Klipper.
 *
 * Garante sincronização entre layouts/app.vue (handlers reais de teclado)
 * e components/ui/CommandPalette.vue (badges visuais de atalho).
 */

import type { ModalName } from '~/composables/useModal'

export type ShortcutDefinition =
  | { key: string; label: string; description: string; actionType: 'modal'; target: ModalName }
  | { key: string; label: string; description: string; actionType: 'route'; target: string }

export const GLOBAL_SHORTCUTS = {
  NOVO_LANCAMENTO: {
    key: 'n',
    label: 'N',
    description: 'Novo Lançamento',
    actionType: 'modal',
    target: 'novo-lancamento',
  },
  DASHBOARD: {
    key: 'd',
    label: 'D',
    description: 'Painel',
    actionType: 'route',
    target: '/dashboard',
  },
  TRANSACOES: {
    key: 't',
    label: 'T',
    description: 'Lançamentos',
    actionType: 'route',
    target: '/transacoes',
  },
  ORCAMENTO: {
    key: 'o',
    label: 'O',
    description: 'Orçamento',
    actionType: 'route',
    target: '/orcamento',
  },
  IMPORTAR: {
    key: 'i',
    label: 'I',
    description: 'Importar Extrato/Fatura',
    actionType: 'route',
    target: '/importar',
  },
} as const satisfies Record<string, ShortcutDefinition>
