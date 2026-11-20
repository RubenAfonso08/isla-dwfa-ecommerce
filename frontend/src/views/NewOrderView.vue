<script setup lang="ts">
// Formulário de encomenda: linhas (produto, quantidade), total em `computed` SÓ para mostrar,
// erros 400 do serializer AO LADO do campo (≈ form.errors["quantity"]).
// Order form: lines (product, quantity), a `computed` total ONLY for display, 400 errors
// from the serializer NEXT TO the field (≈ form.errors["quantity"]).
//
// O backend de referência (Ficha 03) não tem escrita aninhada: POST /orders/ e depois um
// POST /order-items/ por linha. Quem fez o opcional da Ficha 02 manda `items` num só pedido.
// The reference backend has no nested write: POST /orders/ then one POST /order-items/ per
// line. Those who did the Ficha 02 optional send `items` in a single request.
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, unwrap, ApiError } from '@/api/client'
import { useFetch } from '@/composables/useFetch'
import type { Paginated, Product } from '@/types'

const router = useRouter()

// o catálogo para o <select> (página 1 chega para a demo · page 1 is enough for the demo)
const { data: catalogue, status } = useFetch<Paginated<Product>>(() =>
  unwrap(
    api.GET('/api/v1/products/', { params: { query: { in_stock: true, ordering: 'name' } } }),
  ) as Promise<Paginated<Product>>, // ver types.ts · see types.ts
)

interface Line {
  product: number | null
  quantity: number
  error: string | null // o erro do serializer para ESTA linha · the serializer error for THIS line
}
const lines = ref<Line[]>([{ product: null, quantity: 1, error: null }])
const submitting = ref(false)
const formError = ref<string | null>(null)

const money = new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' })
const priceOf = (id: number | null) => Number(catalogue.value?.results.find((p) => p.id === id)?.price ?? 0)
// cosmético: o total que conta é o que a API calcula · cosmetic: the total that counts is the API's
const total = computed(() => lines.value.reduce((sum, l) => sum + priceOf(l.product) * l.quantity, 0))

function addLine() {
  lines.value.push({ product: null, quantity: 1, error: null })
}
function removeLine(i: number) {
  lines.value.splice(i, 1)
}

async function submit() {
  submitting.value = true
  formError.value = null
  lines.value.forEach((l) => (l.error = null))
  try {
    // sem corpo: `customer` vem do token, `status` é `pending` — tudo decidido no servidor
    // no body: `customer` comes from the token, `status` is `pending` — all decided server-side
    const order = await unwrap(
      api.POST('/api/v1/orders/', {
        body: { reference: `ORD-${Date.now()}`, shipping_address: 'Morada de demonstração' } as never,
      }),
    )
    for (const line of lines.value) {
      try {
        await unwrap(
          api.POST('/api/v1/order-items/', {
            body: { order: order.id, product: line.product ?? 0, quantity: line.quantity },
          }),
        )
      } catch (e) {
        // 400: o erro vai para a linha certa; outra coisa: para o topo · 400 → the line; else → the top
        if (e instanceof ApiError && e.status === 400) {
          line.error = e.field('quantity') ?? e.field('product') ?? e.detail
        } else throw e
      }
    }
    if (lines.value.some((l) => l.error)) {
      formError.value = `Order #${order.id} was created but some lines were rejected — fix them or go to My orders.`
      return
    }
    await router.push({ name: 'orders' })
  } catch (e) {
    formError.value = e instanceof ApiError ? e.detail : 'Network error'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section>
    <h1>New order</h1>
    <p v-if="status === 'loading'" class="state">Loading catalogue…</p>
    <form v-else-if="catalogue" @submit.prevent="submit">
      <div v-for="(line, i) in lines" :key="i" class="line" :class="{ invalid: line.error }">
        <select v-model="line.product" required>
          <option :value="null" disabled>Choose a product…</option>
          <option v-for="p in catalogue.results" :key="p.id" :value="p.id">
            {{ p.name }} — {{ money.format(Number(p.price)) }} ({{ p.stock }} in stock)
          </option>
        </select>
        <input v-model.number="line.quantity" type="number" min="1" required />
        <span class="line-total">{{ money.format(priceOf(line.product) * line.quantity) }}</span>
        <button type="button" :disabled="lines.length === 1" @click="removeLine(i)">×</button>
        <p v-if="line.error" class="field-error">{{ line.error }}</p>
      </div>
      <p><button type="button" @click="addLine">+ Add line</button></p>
      <p class="total">Total (estimate): <strong>{{ money.format(total) }}</strong></p>
      <p v-if="formError" class="error" role="alert">{{ formError }}</p>
      <button type="submit" :disabled="submitting">{{ submitting ? 'Placing…' : 'Place order' }}</button>
    </form>
  </section>
</template>

<style scoped>
.line {
  display: grid;
  grid-template-columns: 1fr 5rem 6rem 2rem;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.5rem;
}
.line.invalid select,
.line.invalid input {
  border-color: #a40624;
}
.field-error {
  grid-column: 1 / -1;
  margin: 0;
  font-size: 0.8rem;
  color: #a40624;
}
select,
input {
  font: inherit;
  padding: 0.35rem 0.5rem;
}
.line-total {
  text-align: right;
}
.state {
  color: var(--color-text-soft);
}
.error {
  color: #a40624;
}
</style>
