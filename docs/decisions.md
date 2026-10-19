# Decisões · Decisions

PT: uma linha por decisão — o quê, porquê, alternativa rejeitada. Cresce ficha a ficha; o M1/M2/M3 avaliam este ficheiro.
EN: one line per decision — what, why, rejected alternative. Grows ficha by ficha; M1/M2/M3 grade this file.

## Esqueleto · Skeleton

- **`AUTH_USER_MODEL = "accounts.User"` desde o dia zero** — trocar depois da primeira migração obriga a reescrever o histórico; um `AbstractUser` vazio não custa nada. · Declared on day zero; swapping later means rewriting migration history; an empty `AbstractUser` is free.
- **Settings por ambiente (`base/dev/test/prod`) com `django-environ`** — o mesmo código em todos os ambientes, só as variáveis mudam (12-factor); segredos fora do git. · Same code everywhere, only env vars change; secrets stay out of git.
- **`/api/health/` devolve 503, não 500, com a base de dados em baixo** — é o código que um load balancer lê como "tira esta instância de rotação". · 503 is what a load balancer reads as "take this instance out of rotation".

## Ficha 02 — modelos · models

<!-- três decisões: um on_delete, uma constraint, JSONB sim/não · three decisions: one on_delete, one constraint, JSONB yes/no 

--`Product.category` utiliza `PROTECT': impede a eliminação de categorias ainda referenciadas por produtos; não usei `CASCADE` para evitar eliminar o catálogo acidentalmente.

- `Product.sku` tem uma `UniqueConstraint` e `Product.price` uma `CheckConstraint`: a base de dados garante SKUs únicos e preços não negativos mesmo quando a escrita não passa por um formulário.

-  Não utilizei `JSONB`: Os dados do domínio da loja, como produtos, categorias, encomendas e pagamentos, possuem uma estrutura definida e relações explícitas entre entidades. Por esse motivo, optei por utilizar campos tipados e relações relacionais, evitando a utilização de JSONB.

## Ficha 02 — API

<!-- -->
