<script setup lang="ts">
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { API_URL } from '@/api/client'
import { useAuth } from '@/stores/auth'

const auth = useAuth()
const router = useRouter()

function logout() {
  auth.logout()
  router.push({ name: 'products' })
}
</script>

<template>
  <header>
    <RouterLink :to="{ name: 'products' }" class="brand">Shop</RouterLink>
    <nav>
      <RouterLink :to="{ name: 'products' }">Products</RouterLink>
      <RouterLink :to="{ name: 'orders' }">My orders</RouterLink>
    </nav>
    <span class="spacer" />
    <span class="api">API: {{ API_URL }}</span>
    <template v-if="auth.isLoggedIn">
      <span class="user">{{ auth.user?.username }}<span v-if="auth.isGestor"> · gestor</span></span>
      <button @click="logout">Logout</button>
    </template>
    <RouterLink v-else :to="{ name: 'login' }">Login</RouterLink>
  </header>
  <main>
    <RouterView />
  </main>
</template>

<style scoped>
header {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 1rem;
}
.brand {
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--color-accent);
  text-decoration: none;
}
nav {
  display: flex;
  gap: 0.75rem;
}
nav a.router-link-active {
  font-weight: 600;
}
.spacer {
  flex: 1;
}
.api,
.user {
  font-size: 0.8rem;
  color: var(--color-text-soft);
}
</style>
