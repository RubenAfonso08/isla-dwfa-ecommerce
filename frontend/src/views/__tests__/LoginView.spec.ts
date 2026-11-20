// Um 401 mostra a mensagem e NÃO navega · a 401 shows the message and does NOT navigate
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import LoginView from '../LoginView.vue'
import { ApiError } from '@/api/client'

const push = vi.fn<(to: string) => Promise<void>>()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push }),
  useRoute: () => ({ query: { next: '/orders' } }),
}))

const login = vi.fn<(u: string, p: string) => Promise<void>>()
vi.mock('@/stores/auth', () => ({
  useAuth: () => ({ login }),
}))

describe('LoginView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    push.mockReset()
    login.mockReset()
  })

  async function fill(w: ReturnType<typeof mount>) {
    await w.find('input[autocomplete="username"]').setValue('ana')
    await w.find('input[type="password"]').setValue('pass1234')
    await w.find('form').trigger('submit')
    await flushPromises()
  }

  it('shows the error from a 401 and stays on the page', async () => {
    login.mockRejectedValue(new ApiError(401, { type: 'about:blank', title: 'Unauthorized', status: 401 }))
    const w = mount(LoginView)
    await fill(w)
    expect(w.find('[role=alert]').text()).toContain('Invalid username or password')
    expect(push).not.toHaveBeenCalled()
  })

  it('navigates to ?next= after a successful login', async () => {
    login.mockResolvedValue(undefined)
    const w = mount(LoginView)
    await fill(w)
    expect(login).toHaveBeenCalledWith('ana', 'pass1234')
    expect(push).toHaveBeenCalledWith('/orders')
    expect(w.find('[role=alert]').exists()).toBe(false)
  })
})
