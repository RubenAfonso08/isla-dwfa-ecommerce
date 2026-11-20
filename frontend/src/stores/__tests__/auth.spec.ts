// A store testada sem rede: `fetch` substituído por vi.fn() · the store tested without a network
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuth } from '../auth'

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
}

describe('auth store', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('login stores the refresh in localStorage and loads the user', async () => {
    const fetchMock = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse({ access: 'A1', refresh: 'R1' }))
      .mockResolvedValueOnce(jsonResponse({ id: 1, username: 'ana', groups: [] }))
    vi.stubGlobal('fetch', fetchMock)

    const auth = useAuth()
    await auth.login('ana', 'pass1234')

    expect(auth.isLoggedIn).toBe(true)
    expect(auth.user?.username).toBe('ana')
    expect(auth.access).toBe('A1') // só em memória · memory only
    expect(localStorage.getItem('refresh')).toBe('R1')
    expect(localStorage.getItem('access')).toBeNull()
    const [url, init] = fetchMock.mock.calls[0] as [Request, RequestInit?]
    expect(String(url instanceof Request ? url.url : url)).toContain('/api/v1/auth/token/')
    expect(init).toBeUndefined()
    vi.unstubAllGlobals()
  })

  it('a failed login leaves the store empty', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn<typeof fetch>().mockResolvedValue(
        jsonResponse({ type: 'about:blank', title: 'Unauthorized', status: 401 }, 401),
      ),
    )
    const auth = useAuth()
    await expect(auth.login('ana', 'wrong')).rejects.toMatchObject({ status: 401 })
    expect(auth.isLoggedIn).toBe(false)
    expect(localStorage.getItem('refresh')).toBeNull()
    vi.unstubAllGlobals()
  })

  it('logout clears everything', async () => {
    localStorage.setItem('refresh', 'R0')
    const auth = useAuth()
    expect(auth.refresh).toBe('R0')
    auth.logout()
    expect(auth.refresh).toBeNull()
    expect(localStorage.getItem('refresh')).toBeNull()
  })
})
