# E2E — automação (Playwright)

Código da suite E2E. As **specs Gherkin** ficam em [`docs/e2e/`](../../docs/e2e/README.md).

Esta pasta usa Playwright com Python e uma stack Docker isolada.
As seeds pertencem ao Playwright (SQL via `psycopg`), não ao Django.

## Serviços

O profile `e2e` inicia somente quando solicitado:

- `db-e2e`: PostgreSQL sem porta exposta no host
- `web-e2e`: Django conectado exclusivamente ao `db-e2e`
- `playwright`: runner com Chromium e artefatos de falha

Assim, o reset do banco dos testes não altera o banco local de desenvolvimento.

## Execução

```bash
docker compose --profile e2e run --rm playwright
```

Arquivo ou cenário específico:

```bash
docker compose --profile e2e run --rm playwright pytest tests/e2e/test_home.py
```

## Estado do banco (por teste)

A fixture `db` em `conftest.py`:

1. abre uma conexão própria do Playwright
2. faz `TRUNCATE` das tabelas da aplicação
3. aplica seeds em `tests/e2e/db/seeds/`
4. faz `COMMIT` (obrigatório para o `web-e2e` enxergar os dados via HTTP)
5. executa o teste
6. limpa com `TRUNCATE` novamente

**Por que commit + truncate:** no PostgreSQL, outra conexão (a do Django) nunca lê
linhas não commitadas. Em E2E o browser bate no `web-e2e`, então o seed precisa
ser visível.

Adicione seeds específicas do cenário no próprio teste, usando a fixture `db`.

## Artefatos

Em falha, traces/screenshots/vídeos vão para `test-results/` (gitignored).
