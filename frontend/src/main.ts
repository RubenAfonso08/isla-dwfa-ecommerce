import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { api } from './api/client'
import { authMiddleware } from './api/auth'
import { useAuth } from './stores/auth'

const app = createApp(App)

app.use(createPinia())
api.use(authMiddleware) // Bearer em todos os pedidos; 401 → refresh + repetir · Bearer on every request; 401 → refresh + retry

// Arranque: se há refresh guardado, renova e carrega /me/ ANTES de montar — o guard precisa de saber
// Startup: with a stored refresh, renew and load /me/ BEFORE mounting — the guard needs to know
await useAuth().bootstrap()

app.use(router)
app.mount('#app')
