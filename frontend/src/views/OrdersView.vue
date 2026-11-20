<script setup lang="ts">
// "As minhas encomendas": a API já filtra ao cliente autenticado (Ficha 03) — a vista só mostra.
// "My orders": the API already filters to the caller (Ficha 03) — the view only renders.
import { ref } from 'vue'
import { api, unwrap, ApiError } from '@/api/client'
import { useFetch } from '@/composables/useFetch'
import OrderStatusBadge from '@/components/OrderStatusBadge.vue'
import type { Order, Paginated } from '@/types'

const { data, status, error, reload } = useFetch<Paginated<Order>>(() =>
  unwrap(api.GET('/api/v1/orders/', { params: { query: { ordering: '-created_at' } } })),
)

const money = new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' })
const paying = ref<number | null>(null)
const message = ref<string | null>(null) // o 409 é uma mensagem, não um ecrã de erro · a message, not an error screen

async function pay(order: Order) {
  paying.value = order.id
  message.value = null
  try {
    await unwrap(api.POST('/api/v1/orders/{id}/pay/', { params: { path: { id: order.id } } }))
    await reload()
  } catch (e) {
    message.value = e instanceof ApiError ? `Order #${order.id}: ${e.detail}` : 'Network error'
  } finally {
    paying.value = null
  }
}
</script>

<template>
  <section>
    <div class="head">
      <h1>My orders</h1>
      <RouterLink :to="{ name: 'new-order' }" class="button">+ New order</RouterLink>
    </div>

    <p v-if="status === 'loading'" class="state">Loading…</p>
    <p v-else-if="status === 'error'" class="state error">{{ error }} <button @click="reload">Retry</button></p>
    <p v-else-if="data && data.count === 0" class="state">No orders yet.</p>
    <template v-else-if="data">
      <p v-if="message" class="message" role="status">{{ message }}</p>
      <table>
        <thead>
          <tr><th>#</th><th>Date</th><th>Items</th><th>Total</th><th>Status</th><th></th></tr>
        </thead>
        <tbody>
          <tr v-for="o in data.results" :key="o.id">
            <td>{{ o.id }}</td>
            <td>{{ new Date(o.created_at).toLocaleDateString('pt-PT') }}</td>
            <td>{{ o.items.map((i) => `${i.quantity}× ${i.product_name}`).join(', ') }}</td>
            <td>{{ money.format(Number(o.total)) }}</td>
            <td><OrderStatusBadge :status="o.status" /></td>
            <td>
              <button v-if="o.status === 'pending'" :disabled="paying === o.id" @click="pay(o)">
                {{ paying === o.id ? 'Paying…' : 'Pay' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </template>
  </section>
</template>

<style scoped>
.head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}
.button {
  color: var(--color-accent);
  font-weight: 600;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}
th,
td {
  text-align: left;
  padding: 0.4rem 0.5rem;
  border-bottom: 1px solid var(--color-border);
}
.state {
  color: var(--color-text-soft);
}
.error {
  color: #a40624;
}
.message {
  padding: 0.5rem 0.75rem;
  border: 1px solid #8a5a00;
  color: #8a5a00;
  border-radius: 6px;
}
</style>
