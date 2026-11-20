// A store de autenticação (Pinia, setup store) · the auth store (Aula 06).
// PT: `access` só em memória; `refresh` em localStorage (decisão da Aula 04); `user` de /me/.
// EN: `access` in memory only; `refresh` in localStorage (Aula 04 decision); `user` from /me/.

import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { api, unwrap } from '@/api/client'
import type { Me } from '@/types'

const REFRESH_KEY = 'refresh'

export const useAuth = defineStore('auth', () => {
  // estado · state
  const access = ref<string | null>(null)
  const refresh = ref<string | null>(localStorage.getItem(REFRESH_KEY))
  const user = ref<Me | null>(null)
  const ready = ref(false) // o arranque já correu · bootstrap has run

  // getters
  const isLoggedIn = computed(() => user.value !== null)
  const isGestor = computed(() => user.value?.groups.includes('gestores') ?? false)

  function setRefresh(token: string | null) {
    refresh.value = token
    if (token) localStorage.setItem(REFRESH_KEY, token)
    else localStorage.removeItem(REFRESH_KEY)
  }

  // ações · actions
  async function login(username: string, password: string) {
    const pair = await unwrap(api.POST('/api/v1/auth/token/', { body: { username, password } }))
    access.value = pair.access
    setRefresh(pair.refresh) // rotação: cada login dá um refresh novo · rotation
    user.value = await unwrap(api.GET('/api/v1/me/'))
  }

  function logout() {
    access.value = null
    user.value = null
    setRefresh(null)
  }

  /** Troca o refresh por um access novo (e um refresh novo — rotação). null se falhar.
   *  Exchanges the refresh for a new access (and a new refresh — rotation). null on failure. */
  async function refreshAccess(): Promise<string | null> {
    if (!refresh.value) return null
    const { data } = await api.POST('/api/v1/auth/token/refresh/', {
      body: { refresh: refresh.value },
    })
    if (!data) {
      logout()
      return null
    }
    access.value = data.access
    // com ROTATE_REFRESH_TOKENS a API devolve também um refresh novo (o antigo vai para a blacklist)
    // with ROTATE_REFRESH_TOKENS the API also returns a new refresh (the old one is blacklisted)
    if (data.refresh) setRefresh(data.refresh)
    return data.access
  }

  /** No arranque: se há refresh guardado, renova e carrega /me/ antes de mostrar o ecrã.
   *  On startup: if a refresh is stored, renew it and load /me/ before showing the screen. */
  async function bootstrap() {
    if (refresh.value && (await refreshAccess())) {
      const { data } = await api.GET('/api/v1/me/')
      user.value = data ?? null
    }
    ready.value = true
  }

  return { access, refresh, user, ready, isLoggedIn, isGestor, login, logout, refreshAccess, bootstrap }
})
