<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="cp-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="Busca e comandos rápidos"
      @click.self="emit('close')"
      @keydown.esc="emit('close')"
    >
      <div ref="dialogRef" class="cp-dialog" @keydown="handleKeyDown">
        <!-- Input bar -->
        <div class="cp-input-wrap">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="cp-search-icon" aria-hidden="true">
            <circle cx="7" cy="7" r="4.5" stroke="currentColor" stroke-width="1.5" />
            <path d="M10.5 10.5L13.5 13.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
          </svg>
          <input
            v-model="query"
            type="text"
            role="combobox"
            aria-autocomplete="list"
            aria-expanded="true"
            aria-controls="cp-results-list"
            :aria-activedescendant="activeItemId"
            placeholder="O que você deseja fazer? (ou digite para filtrar)"
            class="cp-input"
            aria-label="Buscar comandos ou navegar"
            autofocus
          />
          <span class="cp-esc-hint" @click="emit('close')">ESC</span>
        </div>

        <!-- Results list -->
        <div id="cp-results-list" class="cp-results" role="listbox">
          <div v-if="filteredItems.length === 0" class="cp-empty">
            Nenhum comando ou página encontrada para "{{ query }}".
          </div>

          <template v-else>
            <button
              v-for="(item, idx) in filteredItems"
              :id="`cp-item-${item.id}`"
              :key="item.id"
              type="button"
              class="cp-item"
              :class="{ active: selectedIndex === idx }"
              role="option"
              :aria-selected="selectedIndex === idx"
              @mouseenter="selectedIndex = idx"
              @click="executeItem(item)"
            >
              <div class="cp-item-icon" aria-hidden="true">
                <UiAppIcon :name="item.icon" :size="16" />
              </div>
              <div class="cp-item-body">
                <div class="cp-item-title">{{ item.title }}</div>
                <div v-if="item.subtitle" class="cp-item-sub">{{ item.subtitle }}</div>
              </div>
              <span v-if="item.badge" class="cp-item-badge">{{ item.badge }}</span>
              <span v-if="item.shortcut" class="cp-item-shortcut">{{ item.shortcut }}</span>
            </button>
          </template>
        </div>

        <!-- Footer hints -->
        <div class="cp-footer">
          <span class="cp-footer-tip"><kbd>↑</kbd><kbd>↓</kbd> navegar</span>
          <span class="cp-footer-tip"><kbd>↵</kbd> selecionar</span>
          <span class="cp-footer-tip"><kbd>esc</kbd> fechar</span>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { GLOBAL_SHORTCUTS } from '~/composables/useKeyboardShortcuts'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: [] }>()

const router = useRouter()
const { open: openModal } = useModal()

const query = ref('')
const selectedIndex = ref(0)
const dialogRef = ref<HTMLElement | null>(null)
const triggerEl = ref<HTMLElement | null>(null)
const { activate, deactivate } = useFocusTrap(dialogRef)

interface CommandItem {
  id: string
  title: string
  subtitle?: string
  icon: string
  badge?: string
  shortcut?: string
  category: 'action' | 'navigation'
  run: () => void
}

const commands: CommandItem[] = [
  // Ações Rápidas
  {
    id: 'act-novo-lancamento',
    title: 'Novo Lançamento',
    subtitle: 'Registrar entrada ou saída financeira',
    icon: 'income',
    badge: 'Ação',
    shortcut: GLOBAL_SHORTCUTS.NOVO_LANCAMENTO.label,
    category: 'action',
    run: () => openModal(GLOBAL_SHORTCUTS.NOVO_LANCAMENTO.target),
  },
  {
    id: 'act-nova-conta',
    title: 'Cadastrar Nova Carteira / Cartão',
    subtitle: 'Adicionar conta bancária, cartão ou corretora',
    icon: 'wallet',
    badge: 'Ação',
    category: 'action',
    run: () => openModal('nova-conta'),
  },
  {
    id: 'act-novo-aporte',
    title: 'Registrar Aporte em Investimentos',
    subtitle: 'Adicionar ação, FII, renda fixa ou cripto',
    icon: 'investment',
    badge: 'Ação',
    category: 'action',
    run: () => openModal('novo-aporte'),
  },
  {
    id: 'act-nova-categoria',
    title: 'Criar Nova Categoria de Orçamento',
    subtitle: 'Criar envelope e definir limite mensal',
    icon: 'utilities',
    badge: 'Ação',
    category: 'action',
    run: () => openModal('nova-categoria'),
  },
  {
    id: 'act-novo-portador',
    title: 'Adicionar Membro / Portador',
    subtitle: 'Cadastrar titular ou dependente familiar',
    icon: 'health',
    badge: 'Ação',
    category: 'action',
    run: () => openModal('novo-portador'),
  },

  // Navegação
  {
    id: 'nav-dashboard',
    title: 'Ir para o Painel',
    subtitle: 'Visão geral do patrimônio e KPIs do mês',
    icon: 'wallet',
    badge: 'Ir para',
    shortcut: GLOBAL_SHORTCUTS.DASHBOARD.label,
    category: 'navigation',
    run: () => router.push(GLOBAL_SHORTCUTS.DASHBOARD.target),
  },
  {
    id: 'nav-transacoes',
    title: 'Ir para Lançamentos & Extratos',
    subtitle: 'Consultar histórico de transações',
    icon: 'income',
    badge: 'Ir para',
    shortcut: GLOBAL_SHORTCUTS.TRANSACOES.label,
    category: 'navigation',
    run: () => router.push(GLOBAL_SHORTCUTS.TRANSACOES.target),
  },
  {
    id: 'nav-orcamento',
    title: 'Ir para Orçamento & Envelopes',
    subtitle: 'Acompanhar gastos por categoria e limites',
    icon: 'utilities',
    badge: 'Ir para',
    shortcut: GLOBAL_SHORTCUTS.ORCAMENTO.label,
    category: 'navigation',
    run: () => router.push(GLOBAL_SHORTCUTS.ORCAMENTO.target),
  },
  {
    id: 'nav-investimentos',
    title: 'Ir para Investimentos & Carteira',
    subtitle: 'Acompanhar posição patrimonial e rentabilidade',
    icon: 'investment',
    badge: 'Ir para',
    category: 'navigation',
    run: () => router.push('/investimentos'),
  },
  {
    id: 'nav-contas',
    title: 'Ir para Contas, Cartões & Dívidas',
    subtitle: 'Saldos bancários e comparador de juros',
    icon: 'wallet',
    badge: 'Ir para',
    category: 'navigation',
    run: () => router.push('/contas'),
  },
  {
    id: 'nav-importar',
    title: 'Importar Extrato ou Fatura (PDF/CSV)',
    subtitle: 'Itaú, Santander, Nubank e outros',
    icon: 'transfer',
    badge: 'Ir para',
    shortcut: GLOBAL_SHORTCUTS.IMPORTAR.label,
    category: 'navigation',
    run: () => router.push(GLOBAL_SHORTCUTS.IMPORTAR.target),
  },
  {
    id: 'nav-portadores',
    title: 'Ir para Gestão de Portadores',
    subtitle: 'Rateio e visão por membro da família',
    icon: 'health',
    badge: 'Ir para',
    category: 'navigation',
    run: () => router.push('/portadores'),
  },
  {
    id: 'nav-relatorios',
    title: 'Ir para Relatórios & Auditoria',
    subtitle: 'Demonstrativos e visão histórica',
    icon: 'utilities',
    badge: 'Ir para',
    category: 'navigation',
    run: () => router.push('/relatorios'),
  },
]

const filteredItems = computed(() => {
  const q = query.value.toLowerCase().trim()
  if (!q) return commands
  return commands.filter(
    (item) =>
      item.title.toLowerCase().includes(q) ||
      (item.subtitle && item.subtitle.toLowerCase().includes(q))
  )
})

const activeItemId = computed(() => {
  const item = filteredItems.value[selectedIndex.value]
  return item ? `cp-item-${item.id}` : undefined
})

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      query.value = ''
      selectedIndex.value = 0
      triggerEl.value = document.activeElement as HTMLElement
      nextTick(() => activate())
    } else {
      deactivate(triggerEl.value)
    }
  }
)

watch(filteredItems, () => {
  selectedIndex.value = 0
})

function executeItem(item: CommandItem) {
  emit('close')
  item.run()
}

function handleKeyDown(e: KeyboardEvent) {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (filteredItems.value.length > 0) {
      selectedIndex.value = (selectedIndex.value + 1) % filteredItems.value.length
    }
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    if (filteredItems.value.length > 0) {
      selectedIndex.value =
        (selectedIndex.value - 1 + filteredItems.value.length) % filteredItems.value.length
    }
  } else if (e.key === 'Enter') {
    e.preventDefault()
    const selected = filteredItems.value[selectedIndex.value]
    if (selected) {
      executeItem(selected)
    }
  }
}
</script>

<style scoped>
.cp-overlay {
  position: fixed;
  inset: 0;
  background: rgba(4, 9, 15, 0.78);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 80px 16px 20px;
  z-index: 1000;
}

.cp-dialog {
  background: var(--sf);
  border: 1px solid var(--bd2);
  border-radius: 12px;
  width: 100%;
  max-width: 580px;
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 255, 255, 0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.cp-input-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--bd);
  background: var(--sf);
}

.cp-search-icon {
  color: var(--t3);
  flex-shrink: 0;
}

.cp-input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--t1);
  font-size: 15px;
  font-family: inherit;
  outline: none;
}
.cp-input::placeholder {
  color: var(--t4);
}

.cp-esc-hint {
  font-size: 10px;
  font-family: 'Space Grotesk', monospace;
  color: var(--t4);
  background: var(--ly);
  border: 1px solid var(--bd2);
  border-radius: 4px;
  padding: 2px 6px;
  cursor: pointer;
}

.cp-results {
  max-height: 380px;
  overflow-y: auto;
  padding: 8px;
}

.cp-empty {
  padding: 32px 16px;
  text-align: center;
  color: var(--t4);
  font-size: 13px;
}

.cp-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 12px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: var(--t2);
  text-align: left;
  cursor: pointer;
  transition: background 0.1s, color 0.1s;
  font-family: inherit;
}

.cp-item.active {
  background: var(--bdm);
  color: var(--blt);
}

.cp-item-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--ly);
  color: var(--blue);
  flex-shrink: 0;
}

.cp-item.active .cp-item-icon {
  background: var(--blue);
  color: #0e1112;
}

.cp-item-body {
  flex: 1;
  min-width: 0;
}

.cp-item-title {
  font-size: 13.5px;
  font-weight: 500;
  color: var(--t1);
}

.cp-item-sub {
  font-size: 11.5px;
  color: var(--t3);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cp-item-badge {
  font-size: 10px;
  color: var(--t4);
  background: var(--ly);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--bd);
}

.cp-item-shortcut {
  font-size: 10px;
  font-family: 'Space Grotesk', monospace;
  color: var(--t4);
  background: var(--sf);
  border: 1px solid var(--bd2);
  border-radius: 4px;
  padding: 1px 5px;
}

.cp-footer {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 18px;
  border-top: 1px solid var(--bd);
  background: var(--bg);
  font-size: 11px;
  color: var(--t4);
}

.cp-footer-tip kbd {
  margin-right: 4px;
}
</style>
