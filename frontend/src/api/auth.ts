// Middleware de autenticação do openapi-fetch · openapi-fetch auth middleware (Aula 06).
// PT: mete o `Bearer` em todos os pedidos; a um 401 renova o access token UMA vez e
// repete o pedido; se a renovação falhar, a sessão acabou (logout → /login).
// EN: adds `Bearer` to every request; on a 401 refreshes the access token ONCE and
// retries the request; if the refresh fails, the session is over (logout → /login).

import type { Middleware } from 'openapi-fetch'
import { useAuth } from '@/stores/auth'

const SKIP = ['/api/v1/auth/token/', '/api/v1/auth/token/refresh/']

// o pedido original já foi consumido quando chega a resposta: guardamos um clone por id
// the original request is consumed by the time the response arrives: keep a clone per id
const clones = new Map<string, Request>()

export const authMiddleware: Middleware = {
  async onRequest({ request, schemaPath, id }) {
    if (SKIP.includes(schemaPath)) return request
    const auth = useAuth()
    if (auth.access) request.headers.set('Authorization', `Bearer ${auth.access}`)
    clones.set(id, request.clone())
    return request
  },

  async onResponse({ response, schemaPath, id }) {
    const retry = clones.get(id)
    clones.delete(id)
    if (response.status !== 401 || SKIP.includes(schemaPath) || !retry) return response

    const auth = useAuth()
    const access = await auth.refreshAccess() // null = refresh expirado ou inválido · expired/invalid
    if (!access) {
      auth.logout()
      return response
    }
    retry.headers.set('Authorization', `Bearer ${access}`)
    return fetch(retry) // segunda e última tentativa · second and last attempt
  },
}
