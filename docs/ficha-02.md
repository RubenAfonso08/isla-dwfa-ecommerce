# Perguntas de reflexão — Ficha 02

**1.** A validação no serializer pode ser contornada por escritas através do ORM, scripts ou Django Admin. Uma `CheckConstraint` garante regras dentro da base de dados, mas não consegue comparar diretamente o stock de outra tabela. Para evitar vendas concorrentes, devemos bloquear o produto com `select_for_update()` numa transação e voltar a validar o stock antes de o atualizar.

**2.** Usaríamos `CursorPagination` em listas muito grandes e frequentemente percorridas, pois evita o custo de contar todos os registos e permite navegar eficientemente entre páginas. O queryset deve ter uma ordenação estável e consistente, idealmente com um campo único ou um desempate único, como `created_at` e `id`.