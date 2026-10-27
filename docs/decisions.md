# Decisões · Decisions

PT: uma linha por decisão — o quê, porquê, alternativa rejeitada. Cresce ficha a ficha; o M1/M2/M3 avaliam este ficheiro.  
EN: one line per decision — what, why, rejected alternative. Grows ficha by ficha; M1/M2/M3 grade this file.

## Esqueleto · Skeleton

- **`AUTH_USER_MODEL = "accounts.User"` desde o dia zero** — trocar depois da primeira migração obriga a reescrever o histórico; um `AbstractUser` vazio não custa nada. · Declared on day zero; swapping later means rewriting migration history; an empty `AbstractUser` is free.
- **Settings por ambiente (`base/dev/test/prod`) com `django-environ`** — o mesmo código em todos os ambientes, só as variáveis mudam (12-factor); segredos fora do git. · Same code everywhere, only env vars change; secrets stay out of git.
- **`/api/health/` devolve 503, não 500, com a base de dados em baixo** — é o código que um load balancer lê como "tira esta instância de rotação". · 503 is what a load balancer reads as "take this instance out of rotation".

## Ficha 02 — modelos · models

<!-- três decisões: um on_delete, uma constraint, JSONB sim/não · three decisions: one on_delete, one constraint, JSONB yes/no -->

- `Product.category` utiliza `PROTECT`: impede a eliminação de categorias ainda referenciadas por produtos; não usei `CASCADE` para evitar eliminar o catálogo acidentalmente.
- `Product.sku` tem uma `UniqueConstraint` e `Product.price` uma `CheckConstraint`: a base de dados garante SKUs únicos e preços não negativos mesmo quando a escrita não passa por um formulário.
- Não utilizei `JSONB`: os dados do domínio da loja, como produtos, categorias, encomendas e pagamentos, possuem uma estrutura definida e relações explícitas entre entidades. Por esse motivo, optei por utilizar campos tipados e relações relacionais, evitando a utilização de JSONB.

## Ficha 02 — API

- Campos só de leitura: IDs, timestamps, estado da encomenda, total calculado e preço unitário do artigo são controlados pelo servidor, evitando que o cliente altere dados derivados ou de controlo.
- Paginação: utilizei `PageNumberPagination` com 20 resultados por página, permitindo percorrer coleções de recursos sem devolver todos os registos numa única resposta.
- Versionamento: utilizei o prefixo `/api/v1/`, explícito nos URLs e preparado para permitir uma versão futura com alterações incompatíveis.
- Consultas: a listagem de encomendas usa `select_related`, `prefetch_related` e `annotate` para evitar o problema N+1; o teste limita a listagem a três queries.
- Validação: os serializers apresentam erros de validação antes da escrita, enquanto as constraints da base de dados mantêm a integridade dos dados independentemente do caminho de escrita.


## Ficha 03 — Autenticação e autorização

- **JWT:** access token com duração de 30 minutos e refresh token com duração de um dia. Os refresh tokens são rotativos e o token anterior é colocado na blacklist.
- **Armazenamento dos tokens:** para a futura SPA, o access token será mantido em memória e o refresh token em localStorage. Evita-se guardar o access token em armazenamento persistente, embora a proteção contra XSS continue a ser necessária.
- **Papéis:** os gestores são identificados pela pertença ao grupo `gestores`, criado por migração de dados.
- **Catálogo:** as leituras de categorias e produtos são públicas; as operações de escrita são reservadas aos gestores.
- **Clientes:** o endpoint de clientes só é acessível a gestores.
- **Encomendas:** os clientes autenticados só podem consultar e pagar as suas próprias encomendas; os gestores podem consultar todas. O cliente da encomenda é definido pelo servidor.
- **Artigos e pagamentos:** as consultas são limitadas às encomendas do utilizador autenticado, exceto para os gestores.
- **Matriz endpoint × papel:** anónimo, cliente e gestor são testados segundo a tabela seguinte.

| Endpoint | Anónimo | Cliente | Gestor |
|---|---|---|---|
| `GET /api/v1/categories/` | 200 | 200 | 200 |
| `POST /api/v1/categories/` | 401 | 403 | 201 |
| `GET /api/v1/products/` | 200 | 200 | 200 |
| `POST /api/v1/products/` | 401 | 403 | 201 |
| `GET /api/v1/customers/` | 401 | 403 | 200 |
| `GET /api/v1/orders/` | 401 | Só as suas | Todas |
| `GET /api/v1/orders/{id}/`, encomenda alheia | 401 | 404 | 200 |
| `POST /api/v1/orders/{id}/pay/`, encomenda alheia | 401 | 404 | 200, se puder ser paga |
| `GET /api/v1/order-items/` e `/api/v1/payments/` | 401 | Só os seus | Todos |
| `GET /api/v1/me/` | 401 | 200 | 200 |

- **Teste de segurança:** sem o filtro do `get_queryset`, um cliente poderia obter a encomenda de outra pessoa e a resposta poderia confirmar a sua existência através de um `403`. O filtro faz com que essa encomenda não seja encontrada e resulte em `404`.
