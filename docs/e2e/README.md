# E2E — especificação

Esta pasta guarda o **inventário funcional** (Gherkin): o que deve ser testado.

A automação Playwright fica em [`tests/e2e/`](../../tests/e2e/) — como rodar, seeds e código.

## Separação (padrão do projeto)

| Pasta | Conteúdo |
| --- | --- |
| `docs/e2e/` | Specs Gherkin, prioridades, critérios de aceite |
| `tests/e2e/` | Playwright, fixtures, seeds SQL, Docker de teste |

## Cenários

| Arquivo | Escopo | Cenários |
| --- | --- | --- |
| [01_paginas_publicas.feature](01_paginas_publicas.feature) | Home, sobre, navegação, links, arquivos | 12 |
| [02_noticias_eventos_midia.feature](02_noticias_eventos_midia.feature) | Notícias, eventos, calendário, mídia | 15 |
| [03_inscricoes_contato.feature](03_inscricoes_contato.feature) | Inscrições e formulário de contato | 14 |
| [04_autenticacao.feature](04_autenticacao.feature) | Cadastro, login, logout, reset, admin inicial | 20 |
| [05_portal_permissoes.feature](05_portal_permissoes.feature) | Portal do usuário e controle de acesso | 12 |
| [06_painel_admin.feature](06_painel_admin.feature) | Painel, branding, conteúdo, preview | 19 |
| [07_busca_i18n_acessibilidade.feature](07_busca_i18n_acessibilidade.feature) | Busca, idioma, tema e acessibilidade | 16 |

**Total:** 108 cenários (`@p0` 49 · `@p1` 48 · `@p2` 11)

## Convenções

- `@p0` — fluxo crítico (bloqueia release; automatizar primeiro)
- `@p1` — funcional importante
- `@p2` — complementar / UX
- `@functional` — comportamento funcional (não visual puro)
- `Contexto` — pré-condições compartilhadas da Feature

### Identificadores (spec ↔ teste)

Cada cenário ganha um ID estável:

```text
E2E-<arquivo>-<seq>
```

Exemplo para `01_paginas_publicas.feature`:

| Spec | Tag Gherkin | Teste Playwright |
| --- | --- | --- |
| `[E2E-01-001] Visitante acessa a página inicial` | `@e2e-01-001` | `test_e2e_01_001_*` em `tests/e2e/test_01_paginas_publicas.py` |

Regra: o número do arquivo Gherkin (`01`, `02`…) e o prefixo do arquivo de teste (`test_01_…`) são os mesmos.

**Language:** code identifiers in English (same as the Django app). UI assertions, seed content, and Gherkin stay in Portuguese.

## Estratégia de automação

1. Specs vivem aqui e são a fonte da verdade do aceite.
2. Implementação Playwright espelha os arquivos por domínio (`test_home.py`, depois auth, etc.).
3. Começar pelos `@p0`; `@p1`/`@p2` entram depois ou ficam como checklist manual.
4. Seeds e reset de banco são responsabilidade de `tests/e2e/`, não do Django.

## Como rodar a suite

Ver [`tests/e2e/README.md`](../../tests/e2e/README.md).
