// O `urls.py` do frontend · the frontend's `urls.py`.
// Aula 06: rotas de login e encomendas; `meta.requiresAuth` + `beforeEach` = o guard
// (≈ LoginRequiredMixin). O guard protege o ECRÃ; os DADOS protege-os a API (Ficha 03).
// Aula 06: login and order routes; `meta.requiresAuth` + `beforeEach` = the guard
// (≈ LoginRequiredMixin). The guard protects the SCREEN; the API protects the DATA.
import { createRouter, createWebHistory } from 'vue-router'
import ProductsView from '@/views/ProductsView.vue'
import { useAuth } from '@/stores/auth'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: { name: 'products' } },
    { path: '/products', name: 'products', component: ProductsView },
    {
      path: '/products/:id(\\d+)', // ≈ path("products/<int:pk>/")
      name: 'product',
      props: true, // :id → prop `id`
      component: () => import('@/views/ProductView.vue'), // lazy: um chunk só quando a rota bate
    },
    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
    {
      path: '/orders',
      name: 'orders',
      component: () => import('@/views/OrdersView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/orders/new',
      name: 'new-order',
      component: () => import('@/views/NewOrderView.vue'),
      meta: { requiresAuth: true },
    },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue') },
  ],
})

// ≈ @login_required: sem sessão → /login?next=<para onde ia>
// ≈ @login_required: no session → /login?next=<where it was going>
router.beforeEach((to) => {
  const auth = useAuth()
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: 'login', query: { next: to.fullPath } }
  }
})

export default router
