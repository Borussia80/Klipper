import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import MemberCard from '../MemberCard.vue'

describe('MemberCard', () => {
  it('renders the member name', async () => {
    const wrapper = await mountSuspended(MemberCard, {
      props: { name: 'Roberto Milet', relationship: 'titular', spentLabel: 'R$ 894,50' },
    })
    expect(wrapper.text()).toContain('Roberto Milet')
  })

  it('renders "Titular" for relationship titular', async () => {
    const wrapper = await mountSuspended(MemberCard, {
      props: { name: 'Roberto Milet', relationship: 'titular', spentLabel: 'R$ 894,50' },
    })
    expect(wrapper.text()).toContain('Titular')
  })

  it('renders "Dependente" for relationship dependente', async () => {
    const wrapper = await mountSuspended(MemberCard, {
      props: { name: 'Pedro Milet', relationship: 'dependente', spentLabel: 'R$ 0,00' },
    })
    expect(wrapper.text()).toContain('Dependente')
  })

  it('renders the pre-formatted spent label', async () => {
    const wrapper = await mountSuspended(MemberCard, {
      props: { name: 'Roberto Milet', relationship: 'titular', spentLabel: 'R$ 894,50' },
    })
    expect(wrapper.text()).toContain('R$ 894,50')
  })

  it('renders two-letter initials for a two-word name', async () => {
    const wrapper = await mountSuspended(MemberCard, {
      props: { name: 'Roberto Milet', relationship: 'titular', spentLabel: 'R$ 0,00' },
    })
    expect(wrapper.find('.mem-avatar').text()).toBe('RM')
  })

  it('renders a single-letter initial for a one-word name', async () => {
    const wrapper = await mountSuspended(MemberCard, {
      props: { name: 'Pedro', relationship: 'dependente', spentLabel: 'R$ 0,00' },
    })
    expect(wrapper.find('.mem-avatar').text()).toBe('P')
  })

  it('never renders a reembolso-coverage chip', async () => {
    const wrapper = await mountSuspended(MemberCard, {
      props: { name: 'Pedro Milet', relationship: 'dependente', spentLabel: 'R$ 0,00' },
    })
    expect(wrapper.find('.chip').exists()).toBe(false)
  })
})
