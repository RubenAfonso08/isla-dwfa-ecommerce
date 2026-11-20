// O cliente tipado, gerado do OpenAPI · the typed client, generated from OpenAPI (Aula 06).
// PT: `paths` vem de schema.d.ts; um caminho ou um parâmetro de query errados não compilam.
// EN: `paths` comes from schema.d.ts; a wrong path or query parameter does not compile.

import createClient from 'openapi-fetch'
import type { paths } from './schema'
import type { Problem } from '@/types'

export const API_URL: string = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const api = createClient<paths>({
  baseUrl: API_URL,
  headers: { Accept: 'application/json' },
  // o `fetch` global é lido a cada pedido (e não capturado ao criar o cliente) — é o que permite
  // substituí-lo nos testes com `vi.stubGlobal('fetch', vi.fn())`
  // the global `fetch` is read per request (not captured at creation) — that is what lets tests
  // replace it with `vi.stubGlobal('fetch', vi.fn())`
  fetch: (request) => globalThis.fetch(request),
})

export class ApiError extends Error {
  constructor(
    public status: number,
    public problem: Problem | null,
  ) {
    super(problem?.detail ?? problem?.title ?? `HTTP ${status}`)
  }

  /** O erro de um campo do serializer, para mostrar ao lado do input · one field's error, for forms */
  field(name: string): string | null {
    const e = this.problem?.errors?.[name]
    if (e === undefined) return null
    return Array.isArray(e) ? e.join(' ') : String(e)
  }

  /** `errors.detail` (ou `detail`) — a mensagem geral · the general message */
  get detail(): string {
    return this.field('detail') ?? this.problem?.detail ?? this.message
  }
}

// openapi-fetch devolve `{ data, error, response }` e nunca lança. Para o `useFetch`
// (que espera uma Promise<T> que lança) convertemos aqui, uma vez.
// openapi-fetch returns `{ data, error, response }` and never throws. `useFetch` wants a
// Promise<T> that throws, so we convert here, once.
type Result<T> = { data?: T; error?: unknown; response: Response }

export async function unwrap<T>(call: Promise<Result<T>>): Promise<T> {
  const { data, error, response } = await call
  if (!response.ok || data === undefined) {
    // `error` é o corpo já analisado (Problem Details quando a API o produziu) · the parsed body
    throw new ApiError(response.status, (error ?? null) as Problem | null)
  }
  return data
}
