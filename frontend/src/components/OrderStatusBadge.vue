<script setup lang="ts">
// Um `switch` exaustivo sobre o literal union: acrescentar um estado ao TextChoices (e ao
// schema) faz o vue-tsc acusar aqui — ≈ `match` + `assert_never` em Python.
// An exhaustive `switch` over the literal union: add a status to TextChoices (and the
// schema) and vue-tsc fails here — ≈ `match` + `assert_never` in Python.
import { computed } from 'vue'
import type { OrderStatus } from '@/types'

const props = defineProps<{ status: OrderStatus }>()

const label = computed((): string => {
  switch (props.status) {
    case 'pending':
      return 'Pending payment'
    case 'paid':
      return 'Paid'
    case 'cancelled':
      return 'Cancelled'
  }
  // sem `default`: se faltar um caso, `props.status` fica `never` e o TS acusa
  // no `default`: a missing case leaves `props.status` as `never` and TS complains
  return props.status satisfies never
})
</script>

<template>
  <span class="badge" :class="props.status">{{ label }}</span>
</template>

<style scoped>
.badge {
  display: inline-block;
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid currentColor;
}
.pending {
  color: #8a5a00;
}
.paid {
  color: #1b6e3a;
}
.cancelled {
  color: #6b6b6b;
}
</style>
