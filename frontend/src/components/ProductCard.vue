<script setup lang="ts">
// Um componente "burro": recebe um produto (prop), avisa quando é escolhido (emit).
// A "dumb" component: takes a product in (prop), reports a choice out (emit).
import type { Product } from '@/types'

const props = defineProps<{ product: Product }>()
const emit = defineEmits<{ select: [id: number] }>()

const money = new Intl.NumberFormat('pt-PT', { style: 'currency', currency: 'EUR' })
</script>

<template>
  <article class="card" :class="{ out: props.product.stock === 0 }" @click="emit('select', props.product.id)">
    <h3>{{ props.product.name }}</h3>
    <p class="meta">{{ props.product.category_name }} · {{ props.product.sku }}</p>
    <p class="price">{{ money.format(Number(props.product.price)) }}</p>
    <p v-if="props.product.stock === 0" class="stock">Out of stock</p>
    <p v-else class="stock">{{ props.product.stock }} in stock</p>
  </article>
</template>

<style scoped>
.card {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  cursor: pointer;
}
.card:hover {
  border-color: var(--color-accent);
}
.card.out {
  opacity: 0.6;
}
h3 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
}
.meta,
.stock {
  margin: 0;
  font-size: 0.8rem;
  color: var(--color-text-soft);
}
.price {
  margin: 0.25rem 0;
  font-weight: 600;
}
</style>
