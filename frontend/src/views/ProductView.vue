<script setup lang="ts">
// Detalhe por rota: `/products/:id` → `props.id` (o router passa os params como props).
// Detail by route: `/products/:id` → `props.id` (the router passes params as props).
import { api, unwrap } from '@/api/client'
import { useFetch } from '@/composables/useFetch'
import type { Product } from '@/types'

const props = defineProps<{ id: string }>()

const { data: product, status, error } = useFetch<Product>(() =>
  unwrap(
    api.GET('/api/v1/products/{id}/', { params: { path: { id: Number(props.id) } } }),
  ) as Promise<Product>, // ver types.ts: o schema não distingue pedido de resposta · see types.ts
)
</script>

<template>
  <section>
    <p><RouterLink :to="{ name: 'products' }">‹ All products</RouterLink></p>

    <p v-if="status === 'loading'">Loading…</p>
    <p v-else-if="status === 'error'" class="error">{{ error }}</p>
    <template v-else-if="product">
      <h1>{{ product.name }}</h1>
      <p>{{ product.category_name }} · {{ product.sku }} · {{ product.price }} €</p>
      <p>{{ product.stock }} in stock · active: {{ product.is_active }}</p>
      <!-- `{{ }}` escapa sempre · always escapes. v-html = |safe — só com HTML sanitizado na API -->
      <dl v-if="product.attributes && Object.keys(product.attributes).length">
        <template v-for="(value, key) in product.attributes" :key="key">
          <dt>{{ key }}</dt>
          <dd>{{ value }}</dd>
        </template>
      </dl>
    </template>
  </section>
</template>

<style scoped>
.error {
  color: #a40624;
}
dl {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 0.25rem 1rem;
}
dt {
  font-weight: 600;
}
dd {
  margin: 0;
}
</style>
