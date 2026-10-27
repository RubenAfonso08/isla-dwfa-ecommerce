# Reflexão — Ficha 03

1. `401` indica que não existe autenticação válida; `403` indica que o utilizador está autenticado, mas não tem autorização. O `404` para uma encomenda alheia evita confirmar que um identificador existe, reduzindo a possibilidade de enumeração e fuga de informação.
2. O CORS é aplicado pelos browsers e limita determinados pedidos entre origens diferentes; não bloqueia pedidos feitos com curl ou por scripts fora do browser. A proteção efetiva vem da autenticação, das permissões por papel e por objeto, do queryset filtrado e da validação dos dados.