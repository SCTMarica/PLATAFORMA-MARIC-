# Testes E2E

Esta suite usa Playwright com Python e roda em uma stack Docker isolada.
As seeds pertencem ao Playwright (SQL via `psycopg`), não ao Django.

## Serviços

O profile `e2e` inicia somente quando solicitado:

- `db-e2e`: PostgreSQL sem porta exposta no host
- `web-e2e`: Django conectado exclusivamente ao `db-e2e`
- `playwright`: runner com Chromium e os artefatos de falha habilitados

Assim, o reset do banco dos testes não altera o banco local de desenvolvimento.

## Execução

```bash
docker compose --profile e2e run --rm playwright
```

Para executar um arquivo ou cenário específico:

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

**Por que não dá para “não commitar”:** no PostgreSQL, outra conexão (a do Django)
nunca lê linhas não commitadas. Em E2E real o browser bate no `web-e2e`, então o
seed precisa ser visível → commit + truncate é o equivalente seguro ao rollback
de teste unitário.

Adicione seeds específicas do cenário no próprio teste, usando a fixture `db`.

## Artefatos

Em caso de falha, traces, screenshots e vídeos são gravados em `test-results/`
na raiz do projeto. A pasta está no `.gitignore`.
