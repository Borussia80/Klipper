import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import EmptyState from '../EmptyState.vue'

describe('EmptyState.vue', () => {
  it('renderiza a mensagem vinda da prop', async () => {
    const wrapper = await mountSuspended(EmptyState, { props: { message: 'Nenhuma conta cadastrada.' } })

    expect(wrapper.text()).toContain('Nenhuma conta cadastrada.')
  })

  it('aceita marcação pelo slot padrão no lugar da prop', async () => {
    const wrapper = await mountSuspended(EmptyState, {
      slots: { default: () => 'Nenhum cartão com dados de dívida preenchidos.' },
    })

    expect(wrapper.text()).toContain('Nenhum cartão com dados de dívida preenchidos.')
  })

  // O bloco de ações só existe quando há ação: sem isso o estado vazio sem
  // botão ganharia 12px de margem inferior invisível em 5 das 9 telas.
  it('não monta o bloco de ações quando não há slot', async () => {
    const wrapper = await mountSuspended(EmptyState, { props: { message: 'Nenhum ativo registrado.' } })

    expect(wrapper.find('.empty-state-actions').exists()).toBe(false)
  })

  it('monta as ações num container único quando há slot', async () => {
    const wrapper = await mountSuspended(EmptyState, {
      props: { message: 'Nenhum lançamento no período.' },
      slots: { actions: '<button>Adicionar</button><a href="/importar">Importar</a>' },
    })

    const actions = wrapper.get('.empty-state-actions')
    expect(actions.findAll('button, a')).toHaveLength(2)
  })

  it('usa o tamanho md por padrão', async () => {
    const wrapper = await mountSuspended(EmptyState, { props: { message: 'x' } })

    expect(wrapper.get('.empty-state').classes()).toContain('is-md')
  })

  it.each(['sm', 'md', 'lg'] as const)('aplica a classe do tamanho %s', async (size) => {
    const wrapper = await mountSuspended(EmptyState, { props: { message: 'x', size } })

    expect(wrapper.get('.empty-state').classes()).toContain(`is-${size}`)
  })
})
