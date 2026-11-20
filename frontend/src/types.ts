// Os tipos do domínio `shop` (Aula 06): gerados do `schema.yaml` com openapi-typescript
// e re-exportados daqui com nomes curtos — o resto da app não conhece `components[...]`.
// The `shop` domain types (Aula 06): generated from `schema.yaml` by openapi-typescript
// and re-exported here under short names — the rest of the app never sees `components[...]`.
//
// Regenerar · regenerate:  npx openapi-typescript ../schema.yaml -o src/api/schema.d.ts
// (na API: uv run manage.py spectacular --file schema.yaml, sempre que a API mudar)

import type { components } from '@/api/schema'

type S = components['schemas']

export type Category = S['Category']
export type OrderItem = S['OrderItem']
export type Order = S['Order']
export type OrderStatus = S['StatusEnum'] // 'pending' | 'paid' | 'cancelled' = Order.Status
export type Me = S['Me'] // /api/v1/me/ → { id, username, groups }
export type TokenPair = S['TokenObtainPair'] // { access, refresh } (+ username/password no pedido)

// O esquema gerado marca `stock`, `attributes` e `is_active` como opcionais: têm `default` no
// modelo e o drf-spectacular não os põe em `required` (nem com COMPONENT_SPLIT_REQUEST, que só
// separa os `read_only` do pedido). Na resposta vêm sempre — estreitamos o tipo aqui, uma vez,
// e fazemos o `as` onde os dados entram (as três vistas que carregam produtos).
// The generated schema marks `stock`, `attributes` and `is_active` optional: they have model
// defaults and drf-spectacular leaves them out of `required` (even with COMPONENT_SPLIT_REQUEST,
// which only strips `read_only` fields from the request). In responses they are always present —
// we narrow the type here, once, and cast where the data enters (the three product-loading views).
export interface Product extends Omit<S['Product'], 'stock' | 'attributes' | 'is_active'> {
  stock: number
  attributes: Record<string, unknown> // JSONB — sem schema fixo · no fixed schema
  is_active: boolean
}

// PageNumberPagination do DRF · DRF's PageNumberPagination envelope
export interface Paginated<T> {
  count: number
  next?: string | null
  previous?: string | null
  results: T[]
}

// RFC 9457 Problem Details — o envelope de erro da API (Ficha 02); `errors` = serializer.errors
export interface Problem {
  type: string
  title: string
  status: number
  detail?: string
  errors?: Record<string, string[] | string>
}
