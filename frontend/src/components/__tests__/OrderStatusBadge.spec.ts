import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import OrderStatusBadge from '../OrderStatusBadge.vue'
import type { OrderStatus } from '@/types'

describe('OrderStatusBadge', () => {
  it.each<[OrderStatus, string]>([
    ['pending', 'Pending payment'],
    ['paid', 'Paid'],
    ['cancelled', 'Cancelled'],
  ])('renders %s as "%s"', (status, text) => {
    const w = mount(OrderStatusBadge, { props: { status } })
    expect(w.text()).toBe(text)
    expect(w.classes()).toContain(status)
  })
})
