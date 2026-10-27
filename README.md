# isla-dwfa-ecommerce — esqueleto do projeto · project skeleton

**Desenvolvimento Web Full-stack Avançado** · Mestrado em Engenharia Informática · ISLA Gaia · 2026/27 · David Vaz ([@davidmgvaz](https://github.com/davidmgvaz))

**PT** — Ponto de partida do projeto da UC (tema votado: **e-commerce**). Traz o que é igual para toda a gente — modelo de utilizador próprio, `/api/health/`, settings por ambiente, PostgreSQL 16 em Docker, pytest-django, factory_boy, ruff e CI — e **nada** do domínio: esse acrescentam vocês na Ficha 02 (app `shop`), e o M1/M2/M3 constroem-se sobre este repositório.
**EN** — Starting point for the course project (voted theme: **e-commerce**). It carries what is the same for everyone — custom user model, `/api/health/`, per-environment settings, PostgreSQL 16 in Docker, pytest-django, factory_boy, ruff and CI — and **none** of the domain: you add it in Ficha 02 (app `shop`), and M1/M2/M3 are built on this repository.

## Começar · Getting started

**Um repositório por par** · one repository per pair: um dos dois faz *fork* deste repositório (privado, com o par e `davidmgvaz` como colaboradores) · one of you forks this repo (private, with your pair and `davidmgvaz` as collaborators).

```sh
git clone git@github.com:<vosso-utilizador>/isla-dwfa-ecommerce.git
cd isla-dwfa-ecommerce
cp .env.example .env                 # nunca commitar o .env · never commit .env
docker compose up -d                 # PostgreSQL 16 → docker compose ps mostra "healthy"
uv sync                              # .venv com Django + dependências de dev
uv run python manage.py migrate
uv run pytest                        # 4 testes verdes · 4 green tests → podem começar
uv run python manage.py createsuperuser
uv run python manage.py runserver    # http://localhost:8000/api/health/ · /admin/
```

Requisitos · requirements: Python 3.13, [uv](https://docs.astral.sh/uv/), Docker Compose v2, Git. **Porta 5432 ocupada?** · port busy? → `ports: ["5433:5432"]` no `compose.yaml` **e** `:5433` no `DATABASE_URL` do `.env`.

## O que está cá · What is here

```
config/settings/
  base.py      tudo o que é partilhado · everything shared (lê .env via django-environ)
  dev.py       DEBUG, email na consola · console email
  test.py      hasher rápido, email em memória · fast hasher, in-memory email
  prod.py      cabeçalhos de segurança, sem DEBUG · security headers, no DEBUG
accounts/      User(AbstractUser) — AUTH_USER_MODEL = "accounts.User" · UserFactory
core/          GET /api/health/ → 200 {"status":"ok","db":"ok"} · 503 com a BD em baixo · 503 when the DB is down
docs/decisions.md   as vossas decisões, uma linha cada · your decisions, one line each
compose.yaml   PostgreSQL 16 com healthcheck
pytest.ini     DJANGO_SETTINGS_MODULE=config.settings.test · --reuse-db
.github/workflows/ci.yml   ruff + makemigrations --check + pytest, com PostgreSQL de serviço
```

`DJANGO_SETTINGS_MODULE` vem do `.env` (`config.settings.dev`); os testes usam `config.settings.test` (ver `pytest.ini`); `wsgi.py`/`asgi.py` assumem `config.settings.prod`.

## Comandos do dia a dia · Everyday commands

```sh
uv run ruff check . && uv run ruff format .      # lint + formato (o CI falha sem isto · CI fails without it)
uv run python manage.py makemigrations shop --name initial_domain
uv run python manage.py sqlmigrate shop 0001     # ler o SQL antes de aplicar · read the SQL before applying
uv run python manage.py migrate
uv run pytest -x                                 # parar no primeiro erro · stop at first failure
docker compose exec db psql -U dwfa              # \dt · \d+ shop_order
docker compose down -v                           # apagar a base de dados local · wipe the local DB
```

## Regras que ficam para o semestre · Rules for the whole semester

- Segredos nunca no git: `.env` ignorado, `.env.example` commitado com valores fictícios · secrets never in git.
- Modelos referem o utilizador via `settings.AUTH_USER_MODEL`, nunca `User` diretamente · never import `User` directly.
- Migrações commitadas e lidas (`sqlmigrate`) antes de aplicadas · migrations committed and read before applied.
- Sem N+1 nos endpoints de lista; `django_assert_num_queries` nos testes · no N+1 on list endpoints.
- Decisões em `docs/decisions.md`, uma linha cada · decisions in `docs/decisions.md`, one line each.

## Entregas · Deliverables

Ficha 02 · tag `ficha-02-models` (sáb 17/10) e `ficha-02-api` (seg 19/10) · URL do repositório no Moodle até **sex 23/10/2026, 23h59** · M1 09/11 · M2 29/11 · M3 03/01.
