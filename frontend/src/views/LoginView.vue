<script setup lang="ts">
// Login: `v-model` nos campos, `@submit.prevent`, estado "a enviar", erro vindo do Problem Details.
// Login: `v-model` on the fields, `@submit.prevent`, a "submitting" state, error from Problem Details.
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ApiError } from '@/api/client'
import { useAuth } from '@/stores/auth'

const auth = useAuth()
const route = useRoute()
const router = useRouter()

const username = ref('')
const password = ref('')
const submitting = ref(false)
const error = ref<string | null>(null)

async function submit() {
  submitting.value = true
  error.value = null
  try {
    await auth.login(username.value, password.value)
    // de volta para onde ia (?next=), ou para as encomendas · back to ?next=, or to the orders
    const next = typeof route.query.next === 'string' ? route.query.next : '/orders'
    await router.push(next)
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) error.value = 'Invalid username or password.'
    else if (e instanceof ApiError && e.status === 429) error.value = 'Too many attempts — try again in a minute.'
    else error.value = e instanceof ApiError ? e.detail : 'Network error'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="login">
    <h1>Login</h1>
    <form @submit.prevent="submit">
      <label>
        Username
        <input v-model.trim="username" autocomplete="username" required />
      </label>
      <label>
        Password
        <input v-model="password" type="password" autocomplete="current-password" required />
      </label>
      <p v-if="error" class="error" role="alert">{{ error }}</p>
      <button type="submit" :disabled="submitting">
        {{ submitting ? 'Signing in…' : 'Sign in' }}
      </button>
    </form>
    <p class="hint">Seed users: <code>ana</code>, <code>bruno</code>, <code>carla</code> · password <code>pass1234</code></p>
  </section>
</template>

<style scoped>
.login {
  max-width: 24rem;
}
form {
  display: grid;
  gap: 0.75rem;
}
label {
  display: grid;
  gap: 0.25rem;
  font-size: 0.9rem;
}
input {
  font: inherit;
  padding: 0.4rem 0.6rem;
}
.error {
  color: #a40624;
  margin: 0;
}
.hint {
  font-size: 0.8rem;
  color: var(--color-text-soft);
}
</style>
