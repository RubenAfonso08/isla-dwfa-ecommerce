import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ProductCard from '../ProductCard.vue'
import type { Product } from '@/types'

const lamp: Product = {
  id: 7,
  sku: 'SKU-00007',
  name: 'Desk lamp',
  category: 1,
  category_name: 'Lamps',
  price: '19.90',
  stock: 0,
  attributes: {},
  is_active: true,
  created_at: '2026-11-02T19:00:00Z',
}

describe('ProductCard', () => {
  it('renders the product and escapes HTML', () => {
    const w = mount(ProductCard, { props: { product: { ...lamp, name: '<b>Lamp</b>' } } })
    expect(w.text()).toContain('<b>Lamp</b>') // {{ }} escapa · escapes
    expect(w.find('b').exists()).toBe(false)
    expect(w.text()).toContain('Out of stock')
  })

  it('emits select with the id when clicked', async () => {
    const w = mount(ProductCard, { props: { product: lamp } })
    await w.find('article').trigger('click')
    expect(w.emitted('select')).toEqual([[7]])
  })
})
