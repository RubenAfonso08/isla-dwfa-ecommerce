# frontend — a SPA do `shop` · the `shop` SPA (Vue 3 + TypeScript + Vite)

Aulas 05 + 06 (02/11 e 09/11/2026) · Ficha 04, partes 1 e 2 · solução de referência · reference solution. Vive dentro do repositório do projeto, ao lado do Django · lives inside the project repository, next to Django.

**PT** — Criado com `npm create vue@latest frontend` (TypeScript · Router · Pinia · Vitest · ESLint + oxlint · Prettier). **Parte 1 (Aula 05):** lista o catálogo (`/api/v1/products/`, aberto de propósito na Ficha 03) com pesquisa e paginação no URL, e mostra o detalhe por rota (`/products/:id`). **Parte 2 (Aula 06):** tipos gerados do `schema.yaml` (`openapi-typescript`) e cliente `openapi-fetch`; *store* Pinia `auth` (`access` em memória, `refresh` em `localStorage`, `/me/`), *middleware* que envia `Bearer` e a um `401` renova o token **uma vez** e repete o pedido; `LoginView` com `?next=`; *guard* `beforeEach` nas rotas `requiresAuth`; «as minhas encomendas» com *Pagar* (o `409` é uma mensagem) e um formulário de encomenda com os erros `400` do serializer ao lado do campo; `OrderStatusBadge` com `switch` exaustivo; 10 testes Vitest.
**EN** — Scaffolded with `npm create vue@latest frontend` (TypeScript · Router · Pinia · Vitest · ESLint + oxlint · Prettier). **Part 1 (Aula 05):** lists the catalogue (`/api/v1/products/`, deliberately public since Ficha 03) with the search and the page in the URL, and shows the detail by route. **Part 2 (Aula 06):** types generated from `schema.yaml` (`openapi-typescript`) and an `openapi-fetch` client; a Pinia `auth` store (`access` in memory, `refresh` in `localStorage`, `/me/`), a middleware that sends `Bearer` and on a `401` refreshes **once** and retries; `LoginView` with `?next=`; a `beforeEach` guard on `requiresAuth` routes; "my orders" with *Pay* (the `409` is a message) and an order form with the serializer's `400` errors next to the field; an exhaustive-`switch` `OrderStatusBadge`; 10 Vitest tests.

```sh
cd frontend
cp .env.example .env          # VITE_API_URL=http://localhost:8000 — a origem da API · the API origin
npm install
npm run dev                   # http://localhost:5173 — a API tem de estar a correr (uv run manage.py runserver)
npm run type-check            # vue-tsc --build — zero erros · zero errors
npm run test:unit             # Vitest — 10 testes (ProductCard · auth store · LoginView · OrderStatusBadge)
npx openapi-typescript ../schema.yaml -o src/api/schema.d.ts   # regenerar os tipos quando a API mudar · regenerate types
npm run lint                  # oxlint + eslint
npm run build                 # dist/ — vue-tsc + vite build (lazy chunks para ProductView e NotFoundView)
```

## O que está cá · What is here

```
src/
  api/schema.d.ts            GERADO de ../schema.yaml (openapi-typescript): paths + components — não editar · generated, do not edit
  api/client.ts              api = createClient<paths>() (openapi-fetch) · unwrap() → lança ApiError (Problem Details, .field(name))
  api/auth.ts                middleware: Bearer em todos os pedidos; 401 → refreshAccess() uma vez e repete o pedido clonado
  types.ts                   aliases curtos dos tipos gerados (Order, OrderStatus, Me…); Product estreitado (stock/attributes/is_active)
  stores/auth.ts             Pinia setup store: access (memória) · refresh (localStorage) · user (/me/) · login/logout/refreshAccess/bootstrap
  composables/useFetch.ts    os três estados (loading · error · data) uma vez; watchEffect re-executa quando as dependências mudam
  components/ProductCard.vue defineProps<{ product: Product }>() · defineEmits<{ select: [id: number] }>() — "burro", testado
  components/OrderStatusBadge.vue  switch exaustivo sobre OrderStatus (sem default → `satisfies never`)
  views/ProductsView.vue     lista: ?search= e ?page= vivem no URL (computed get/set sobre route.query); pager com next/previous
  views/ProductView.vue      detalhe: /products/:id → prop id (props: true); 404 da API → estado de erro
  views/LoginView.vue        v-model · @submit.prevent · submitting · 401/429 → mensagem · router.push(?next ?? '/orders')
  views/OrdersView.vue       GET /orders/ (a API filtra ao cliente) · Pagar → POST /orders/{id}/pay/ · 409 = mensagem, não ecrã de erro
  views/NewOrderView.vue     linhas (produto, quantidade) · total em computed só para mostrar · POST /orders/ + POST /order-items/ por linha · erros 400 ao lado do campo
  views/NotFoundView.vue     /:pathMatch(.*)*
  router/index.ts            o urls.py do frontend; rotas lazy; meta.requiresAuth + beforeEach → /login?next= (o guard protege o ECRÃ)
  App.vue · main.ts          nav com Login/Logout; createPinia() · api.use(authMiddleware) · await auth.bootstrap() ANTES de montar
env.d.ts                     ImportMetaEnv tipado (VITE_API_URL)
```

## O que se verifica · What to check

**Parte 1**

1. `npm run dev` + a API a correr → `/products` lista **20 de 40** produtos do `seed`; a pesquisa escreve `?search=` no URL e a API devolve só esses (`SKU-0000` → 10) · the URL carries the search; the API filters.
2. «Next» → `?page=2`; recarregar mantém a pesquisa e a página · reload keeps the state because it is in the URL.
3. Clicar num cartão → `/products/<id>`; `ProductView-….js` só é descarregado nessa altura · the detail chunk loads lazily.
4. `/products/99999` → 404 Problem Details → estado de erro · the error state.
5. Um nome com `<b>…</b>` aparece como **texto** (`ProductCard.spec.ts`) · `{{ }}` always escapes.
6. Sem CORS na API a lista fica em «Network error» — é a Ficha 03 a ser necessária · without CORS the list never loads.

**Parte 2**

7. `api.GET('/api/v1/products/', { params: { query: { search: 'lamp' } } })` compila; `query: { foo: 1 }` **não** — os parâmetros vêm do `schema.yaml` · the query params come from the schema.
8. `/orders` sem sessão → `/login?next=/orders`; depois do login volta a `/orders`; `/products` continua acessível sem login · the guard.
9. Login como `ana` / `pass1234`: DevTools → *Pinia* → `auth`: `user` preenchido, `access` presente; *Application* → *Local Storage*: só `refresh` · access in memory, refresh in storage.
10. F5 em `/orders`: a app renova o token no arranque (`POST /auth/token/refresh/`) e fica autenticada — ninguém faz login a cada F5 · bootstrap.
11. `ACCESS_TOKEN_LIFETIME` a 1 min na API: passado 1 min, o pedido seguinte dá `401`, o *middleware* renova e repete — no separador *Network* vêem-se três pedidos · refresh once and retry.
12. `/orders` lista as 10 encomendas da `ana` (a API filtra); *Pagar* numa `pending` → `paid`; *Pagar* outra vez (ou numa `paid`) → a mensagem do `409`, não um ecrã de erro · 409 as a message.
13. `/orders/new`: duas linhas → a encomenda aparece no topo com o total **da API**; uma quantidade acima do stock → «Only N in stock.» ao lado da linha · the field error.
14. `npm run test:unit` → 10 verdes; `type-check`, `lint`, `build` limpos — é o que o CI do M2 vai correr · what the M2 CI runs.
15. Credenciais erradas → «Invalid username or password.»; 11 tentativas num minuto → «Too many attempts» (`429`, Ficha 03) · the throttle.

## Erros comuns · Common mistakes

- `price` tratado como `number` — o DRF serializa `DecimalField` como **string** (`"9.90"`); `Number(...)` antes de formatar · DRF decimals are strings.
- Estado da pesquisa só num `ref` — recarregar perde-o e o *link* não é partilhável; pôr no `route.query` · keep it in the URL.
- `v-model` sem `.lazy` numa pesquisa que chama a API → um pedido por tecla (sem *debounce*) · one request per keystroke.
- `fetch` sem `res.ok` — um 404/500 chega como JSON «válido» e rebenta mais à frente · check `res.ok`.
- `useFetch` com `onMounted` em vez de `watchEffect` → mudar `?page=` não recarrega · the load has to re-run when its inputs change.
- `VITE_API_URL` sem o prefixo `VITE_` → `undefined` no browser (o Vite só expõe `VITE_*`) · only `VITE_*` reaches the browser.
- Segredos em `.env` do frontend — vão para o `dist/` · the bundle is public.
- `.env` do frontend commitado (o `.gitignore` da raiz já ignora `.env` em qualquer pasta) · never commit it.
- Guardar o `access` em `localStorage` «porque é mais fácil» — a decisão da Aula 04 é `access` em memória, `refresh` em `localStorage`; escrever porquê em `decisions.md` · access in memory, refresh in storage, and say why.
- Renovar o token em *loop*: um `401` na própria renovação tem de terminar em `logout()`, nunca em nova renovação · refresh once; a 401 on the refresh itself ends the session.
- O *guard* como «segurança»: ele esconde o **ecrã**; quem remove o *guard* nas DevTools continua a receber `401` da API — a segurança é a Ficha 03 · the guard hides the screen; the API protects the data.
- `openapi-fetch` com `body: { username, password }` a não compilar — o schema tinha um só componente para pedido e resposta; `COMPONENT_SPLIT_REQUEST: True` no drf-spectacular gera `TokenObtainPairRequest` sem os `read_only` · split request/response components.
- Somar o total com `Number(price)` **e usá-lo** — é só para mostrar; o total que conta é o da API (`Decimal`) · the API's total is the one that counts.
- Mostrar os erros `400` só no topo — `problem.errors.quantity` tem o campo; mostrar ao lado dele · field errors next to the field.
