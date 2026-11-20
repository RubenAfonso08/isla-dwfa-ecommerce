<script setup lang="ts">
// Lista de produtos: pesquisa (`?search=`) e página (`?page=`) vivem no URL.
// Product list: the search and the page live in the URL, not only in memory.
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, unwrap } from '@/api/client'
import { useFetch } from '@/composables/useFetch'
import ProductCard from '@/components/ProductCard.vue'
import type { Paginated, Product } from '@/types'

const route = useRoute()
const router = useRouter()

// o URL é a fonte de verdade; o input escreve nele · the URL is the source of truth
const search = computed({
  get: () => String(route.query.search ?? ''),
  set: (value) => router.replace({ query: { ...route.query, search: value || undefined, page: undefined } }),
})
const page = computed(() => Number(route.query.page ?? 1))

// `useFetch` re-executa `load` quando `search` ou `page` mudam (watchEffect)
// `params.query` é verificado pelo compilador: `{ foo: 1 }` não compila · checked by the compiler
const { data, status, error, reload } = useFetch<Paginated<Product>>(() =>
  unwrap(
    api.GET('/api/v1/products/', {
      params: { query: { search: search.value || undefined, page: page.value } },
    }),
  ) as Promise<Paginated<Product>>, // o schema marca `stock` opcional; na resposta vem sempre (ver types.ts)
)

const pages = computed(() => (data.value ? Math.ceil(data.value.count / 20) : 0))

function goTo(p: number) {
  router.push({ query: { ...route.query, page: p === 1 ? undefined : p } })
}
function open(id: number) {
  router.push({ name: 'product', params: { id } })
}
</script>

<template>
  <section>
    <h1>Products</h1>
    <input v-model.lazy="search" type="search" placeholder="Search by name or SKU…" />

    <p v-if="status === 'loading'" class="state">Loading…</p>
    <p v-else-if="status === 'error'" class="state error">
      {{ error }} <button @click="reload">Retry</button>
    </p>
    <template v-else-if="data">
      <p class="state">{{ data.count }} products · page {{ page }} of {{ pages }}</p>
      <div class="grid">
        <ProductCard v-for="p in data.results" :key="p.id" :product="p" @select="open" />
      </div>
      <nav class="pager">
        <button :disabled="!data.previous" @click="goTo(page - 1)">‹ Previous</button>
        <button :disabled="!data.next" @click="goTo(page + 1)">Next ›</button>
      </nav>
    </template>
  </section>
</template>

<style scoped>
input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  margin: 0.5rem 0 1rem;
  font: inherit;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.75rem;
}
.state {
  color: var(--color-text-soft);
}
.error {
  color: #a40624;
}
.pager {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}
</style>
